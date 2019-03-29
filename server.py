import socket
import sys
import struct

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('127.0.0.1', 4444)
#server_address = ('localhost', 4444)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            # Receive the size of the PCL
            data = connection.recv(8)
            if data:
              # Check endianess of PC with: `lscpu | grep "Byte Order"`
              pcl_size = int.from_bytes(data, byteorder='little')
              print('Received pcl of size: {!r}'.format(pcl_size))
            
              for i_pt in range(0, pcl_size):
                #print(i_pt)
                x = struct.unpack('f', connection.recv(4))
                y = struct.unpack('f', connection.recv(4))
                z = struct.unpack('f', connection.recv(4))

                print((x, y, z))
              print('Finished first pcl')
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
