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

def parse_http_request(header):
    lines = header.split('\n')

    # remove witespace at ends
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

    # these will get set in a bit
    URI_and_proto = ""
    host = ""

    for line in lines:
        if line[:3] == 'GET':
            URI_and_proto = line[3:].strip()
        if line[:7] == 'CONNECT':
            URI_and_proto = line[7:].strip()
        if line[:5].lower() == 'host:':
            host = line[5:].strip()

    print URI_and_proto
    print host

# this handles a single client
def handle_thread(sock, address):
    input_buffer = bytearray()
    while len(input_buffer) < 4 or input_buffer[-4:] != b'\r\n\r\n':
        input_buffer.extend(receive_from_stream(sock, 1)) # i know pulling one byte at a time is slow; it works for now though

    # we now have a complete HTTP request header


    parse_http_request(input_buffer.decode("utf-8"))
    #print len(input_buffer), input_buffer.decode("utf-8")


    sock.close()


def main():
    sock = socket(AF_INET, SOCK_STREAM)
    port = 12235
    sock.bind(('', port))
    sock.listen(10) # queue up to 10 requests

    print "waiting for connections..."

    while True:
        client_sock, client_addr = sock.accept()
        print 'Got connection from', client_addr
        thread.start_new_thread(handle_thread, (client_sock, client_addr))



if __name__ == '__main__':
    main()