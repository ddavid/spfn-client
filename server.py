import os, sys

BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, 'SPFN/spfn'))

import collections
import socket
import struct
import _thread
import threading
import numpy as np

import argparse

import train

class SPFNServer(object):
    def __init__(self, ip_address="127.0.0.1", port=4445, queue_length=10):
        self.queue = collections.deque
        self.queue.maxlen = queue_length
        self.condition = threading.Condition()
        self.connections = []

        # Create a TCP/IP socket
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the port
        server_address = (ip_address, port)
        print('starting up on {} port {}'.format(*server_address))
        self.skt.bind(server_address)

    def pcl_consumer(self):
        self.condition.acquire()
        while True:
            while self.queue:
                pcl = self.queue.popleft()
                self.condition.release()
                ## Predict using SPFN

                self.condition.acquire()
            self.condition.wait()

    def pcl_publisher(self, pcl):
        with self.condition:
            self.queue.append(pcl)
            self.condition.notify()

    # Unterscheidung zwischen PCL Client und UE4 client nötig
    def on_new_client(self, connection, client_address):
        while True:
            # Receive the size of the PCL (size_t)
            data = connection.recv(8)
            if data:
                # Check endianess of PC with: `lscpu | grep "Byte Order"`
                #TODO Check befor Demo!!!
                pcl_size = int.from_bytes(data, byteorder='little')
                print('Received pcl of size: {!r}'.format(pcl_size))
                pcl = np.array([])

                for i_pt in range(0, pcl_size):
                    # Receive single points, represented by floats
                    x = struct.unpack('f', connection.recv(4))
                    y = struct.unpack('f', connection.recv(4))
                    z = struct.unpack('f', connection.recv(4))

                    np.append(pcl, np.array([x, y, z]))

                # Do stuff with PCL using SPFN
                # SPFN output still has to be converted to JSON? to more easily be imported in UE4
                print('PCL saved')
            else:
                print('no data from', client_address)
                break

    def run(self):
        # Listen for incoming connections
        self.skt.listen(1)

        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = self.skt.accept()
            self.connections.append((connection, client_address))
            try:
                _thread.start_new_thread(self.on_new_client, (connection, client_address))
                print('connection from', client_address)

            finally:
                # Clean up the connections
                for client_address in self.connections:
                    print('Closing connection with {} on port {}'.format(*client_address))
                    client_address[0].close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", help="IP Address to start SPFN server on.")
    parser.add_argument(["--port", "-p"], help="Port to bind SPFN Server to", type=int)
    parser.add_argument(["-q", "--queue-length"], help="Length of PCL queue.")
    args = parser.parse_args()

    server = SPFNServer(args.ip, args.port, args.q)
    server.run()
