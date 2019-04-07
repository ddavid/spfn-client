import os, sys, signal

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

from train import SPFN
from signal_handler import ServerSignalHandler


class SPFNServer(object):
    def __init__(self, ip_address="127.0.0.1", port=4445, queue_length=10):
        self.queue = collections.deque([], queue_length)
        print(self.queue.maxlen)
        self.condition = threading.Condition()
        self.connections = []

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
                pcl = self.queue.popleft()
                print("Shape after popping from deque:", pcl.shape, sep=" ")
                self.condition.release()
                ## Predict using SPFN
                bytes_pred_json = self.spfn.predict_single_pcl(pcl)
                # Need a dictionary for connections?
                #TODO Need to differentiate somehow between PCL client and UE4 client
                # Working under the assumption that the UE4 Client will connect later than
                self.skt.sendto(json.dumps(pcl.tolist()), self.connections[1]) # or send floats one by one
                self.skt.sendto(bytes_pred_json, self.connections[1])

                self.condition.acquire()
                # Get rid of items in queue to always have newest
                # Is this necessary with max_length?
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
                # SPFN output still has to be converted to JSON? to more easily be imported in UE4
                #print('PCL saved')
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
            connection, client_address = self.skt.accept()
            self.connections.append((connection, client_address))
            try:
                _thread.start_new_thread(self.on_new_client, (connection, client_address))
            finally:
                print('connection from', client_address)

    def cleanup(self):
        # Clean up the connections
        for client_address in self.connections:
            print('Closing connection with {} on port {}'.format(*client_address))
            client_address[0].close()
        sys.exit(0)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="IP Address to start SPFN server on.")
    parser.add_argument("--port", "-p", help="Port to bind SPFN Server to", type=int)
    parser.add_argument("--queue-length", help="Length of PCL queue.", type=int)
    args = parser.parse_args()
    # Check if called with arguments
    if len(sys.argv) == 3:
        print("Got Arguments: Initializing SPFNServer")
        server = SPFNServer(args.ip, args.port, args.queue_length)
    else:
        print("No args: Default initialization of SPFNServer")
        server = SPFNServer()
    server.run()