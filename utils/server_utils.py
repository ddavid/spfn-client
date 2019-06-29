import json
import pickle
# Do we need this import here?
import socket
import struct
from itertools import chain


def flatten_list(iterable):
    return list(chain.from_iterable(iterable))


def dump_serialized_json_obj(json_obj, save_file=''):
    # Check if string is not empty
    if save_file:
        with open(save_file + '.json', 'w') as json_file:
            json_file.write(json_obj['pred_dict'])
            print('Saved Serialized JSON predictions to %s' % save_file)

        with open(save_file + '_pcl.json', 'w') as pcl_file:
            pcl_file.write(json.dumps(json_obj['point_cloud']))
            print('Saved Serialized PC to %s' % (save_file + '_pcl.json'))

    serialized_json_obj = pickle.dumps(json_obj)

    return serialized_json_obj


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msg_length = struct.unpack('>I', raw_msglen)[0]  # type: Integer
    # Read the message data
    return recvall(sock, msg_length)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = []
    #data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.append(packet)
    # Join Received streamed data at once to avoid overhead from
    bin_data = b''.join(data)
    return bin_data