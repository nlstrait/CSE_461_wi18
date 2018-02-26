from socket import *               # Import socket module
import thread
import random
from  struct import *
import string # for the random character generation

# reliably pulls a given number of bytes from a stream socket
def receive_from_stream(sock, num_bytes):
    buf = bytearray()
    received = bytearray()

    while len(received) < num_bytes:
        buf = sock.recv(num_bytes - len(received))
        received.extend(buf)

    return received

# this handles a single client
def handle_thread(sock, message, address):
    # handle new client

def main():
    sock = socket(AF_INET, SOCK_DGRAM)
    port = 12235
    sock.bind(('', port))

    while True:
        message, address = sock.recvfrom(4096)
        print 'Got connection from', address
        thread.start_new_thread(handle_thread, (sock, message, address))



if __name__ == '__main__':
    main()