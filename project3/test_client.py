from socket import *
import random
import struct
from  struct import pack, unpack
import sys

#IP = "attu2.cs.washington.edu"
IP = "127.0.0.1"

# this also verifies the length and padding of the packet
def verify_header(message, psecret, step, sid):
    if len(message) < 12:
        return False

    if len(message) % 4 != 0:
        return False

    payload_len, secret, step_num, student_id = unpack('!IIHH', message[0:12])
    if len(message) - 12 < payload_len:
        return False

    if secret != psecret:
        return False

    if step_num != step:
        return False

    if student_id != sid:
        return False

    print 'header verified'

    return True


# this extracts the payload length, secret, and step number, and returns them in that order
def parse_header(message):
    return unpack('!IIH', message[0:10])


# helper function to generate a new packet header
def generate_header(payload_len, secret, step_num, sid):
    header = bytearray()
    header.extend(pack('!IIHH', payload_len, secret, step_num, sid))
    return header


# reliably pulls a given number of bytes from a stream socket
def receive_from_stream(sock, num_bytes):
    buf = bytearray()
    received = bytearray()

    while len(received) < num_bytes:
        buf = sock.recv(num_bytes - len(received))
        received.extend(buf)

    return received

def main():

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('127.0.0.1', 12235))

    sock.send(b'GET http://courses.cs.washington.edu/courses/cse461/15au/assignments/project2/simple.html\r\nHost: courses.cs.washington.edu\r\n\r\n')

    response = ""
    while True:
        b = sock.recv(65535)
        if not b:
            break
        response += b
    print response
    


if __name__ == '__main__':
    main()
