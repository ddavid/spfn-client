import os, sys, signal
from socket import socket

BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, 'SPFN/spfn'))
sys.path.append(os.path.join(BASE_DIR, 'utils/'))

import collections
import socket
import struct
import _thread
import threading
import json
import numpy as np

import argparse

import server_utils

from train import SPFN
from signal_handler import ServerSignalHandler


class SPFNServer(object):
    def __init__(self, ip_address="127.0.0.1", port=4445, queue_length=10):
        self.queue = collections.deque([], queue_length)
        print('Starting with point cloud queue of size %i' % self.queue.maxlen)
        self.condition = threading.Condition()
        self.connections = []
        self.connections_dict = {}
        self.connection_count = 0

        # Create Signal Handler for eventual clean up
        self.sig_handler = ServerSignalHandler(self)

        # Create a TCP/IP socket
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.spfn = SPFN()

        # Bind the socket to the port
        server_address = (ip_address, port)
        print('starting up on {} port {}'.format(*server_address))
        self.skt.bind(server_address)

    def pcl_consumer(self):
        self.condition.acquire()
        while True:
            if self.queue:
                ue_package = {}
                pcl_ue_package = {}
                pcl = self.queue.popleft()
                print("Shape after popping from deque:", pcl.shape, sep=" ")
                self.condition.release()
                # Predict using SPFN
                pred_json = self.spfn.predict_single_pcl(pcl)

                # Create object with predicted pcl and prediction results
                pcl_ue = json.dumps(server_utils.flatten_list(pcl.tolist()))

                ue_package['point_cloud'] = pcl_ue
                pcl_ue_package['point_cloud'] = pcl_ue
                ue_package['pred_dict'] = pred_json

                # bytes_pred_json = server_utils.dump_serialized_json_obj(ue_package, save_file='last_pred')
                # test pcl only bytes --> Only garbled output in UE
                # bytes_pred_json = server_utils.dump_serialized_json_obj(pcl_ue)
                # test pcl only bytes --> Only garbled output in UE
                # print(json.dumps(pcl_ue_package))
                bytes_pred_json = server_utils.dump_serialized_json_obj(pcl_ue_package)
                print('Size of bytes obj: %i' % len(bytes_pred_json))


                # Working under the assumption that the UE4 Client will connect
                # later than PCLServer and before first packet is sent

                # Only send to UE client if we are connected to it
                if 'ue_client' in self.connections_dict:
                    print(self.connections_dict['ue_client'])
                    connection, client_address = self.connections_dict['ue_client']
                    connection.send(bytes_pred_json)
                    #self.connections_dict['ue_client'].send(bytes_pred_json)

                self.condition.acquire()
                # Get rid of items in queue to always have newest
            while self.queue:
                self.queue.popleft()
            self.condition.wait()

    def pcl_publisher(self, pcl):
        with self.condition:
            # pop np.array because we have to give it as list(np.array) to construct the Thread
            self.queue.append(pcl)
            self.condition.notify()

    # Unterscheidung zwischen PCL Client und UE4 client nötig
    def on_new_client(self, connection, client_address):
        while True:
            # Receive the size of the PCL (size_t)
            data = connection.recv(8)
            if data:
                # Check endianess of PC with: `lscpu | grep "Byte Order"`
                #TODO Check before Demo!!!
                pcl_size = int.from_bytes(data, byteorder='little')
                #print('Received pcl of size: {!r}'.format(pcl_size))
                pcl = []

                for i_pt in range(0, pcl_size):
                    # Receive single points, represented by floats
                    # Use subscript index 0 because return value is (p,)
                    x = struct.unpack('f', connection.recv(4))[0]
                    y = struct.unpack('f', connection.recv(4))[0]
                    z = struct.unpack('f', connection.recv(4))[0]

                    pcl.append([x, y, z])

                pcl = np.array(pcl)
                #print('Shape of PCL Numpy Array:' , pcl.shape, sep=" ")
                # Publish PCL by appending to queue
                threading.Thread(target=self.pcl_publisher, args=[pcl], name="Zenfone: PCL publisher").start()
            else:
                print('no data from', client_address)
                break

    def run(self):
        # Start PCL Consumer/SPFN thread
        threading.Thread(target=self.pcl_consumer, name='SPFN: PCL Consumer').start()

        # Listen for incoming connections
        self.skt.listen(1)
        while True:
            # Wait for a connection
            print('waiting for a connection')
            socket_tuple = self.skt.accept()
            _, client_address = socket_tuple
            #self.connections.append(socket_tuple)
            # Testing simple Connection Dictionary
            if self.connection_count is 0:
                self.connections_dict['pcl_server'] = socket_tuple
            elif self.connection_count is 1:
                self.connections_dict['ue_client'] = socket_tuple
            try:
                _thread.start_new_thread(self.on_new_client, socket_tuple)
            finally:
                self.connection_count = self.connection_count + 1
                print('connection from', client_address)
                print('Connected to %i clients' % self.connection_count)

    def cleanup(self):
        # Clean up the connections
        try:
            for key, (socket, address) in self.connections_dict.items():
                print('Closing %s connection to' % key, end=' ')
                print('Socket on {}:{}'.format(*address))
                socket.close()
        finally:
            sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="IP Address to start SPFN server on.")
    parser.add_argument("--port", "-p", help="Port to bind SPFN Server to", type=int)
    parser.add_argument("--queue-length", help="Length of PCL queue.", type=int)
    args = parser.parse_args()
    # Check if called with arguments
    if len(sys.argv) == 7:
        print("Got Arguments: Initializing SPFNServer")
        server = SPFNServer(args.ip, args.port, args.queue_length)
    else:
        print("No args: Default initialization of SPFNServer")
        server = SPFNServer()
    server.run()