from socket import *               # Import socket module
import thread
import os
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


    is_get_request = True
    for line in lines:
        if line[:3] == 'GET':
            URI_and_proto = line[3:].strip()
            first_line = line
        if line[:7] == 'CONNECT':
            URI_and_proto = line[7:].strip()
            first_line = line
            is_get_request = False
        if line[:5].lower() == 'host:':
            host = line[5:].strip()


    # get first element of the line
    URI = URI_and_proto.split()[0]

    URI_elements = URI.split(':')

    # http or https
    protocol = URI_elements[0]
    host_elements = host.split(':')

    port = 0
    if len(URI_elements) > 2:
        port = int(URI_elements[-1].split('/')[0]) # the port might have stuff after it, so just take the port number
    elif len(host_elements) > 1:
        port = int(host_elements[-1])
    elif protocol == 'http':
        port = 80
    else:
        port = 443


    # build and return modified header
    return_header = ""
    for line in lines:
        if line[:3].lower() == 'get':
            return_header += line[:-1] + '0\r\n'
        elif len(line) > 10 and line[:11].lower() == 'connection:':
            return_header += 'Connection: close\r\n'
        elif len(line) > 17 and line[:17].lower() == 'proxy-connection:':
            return_header += 'Proxy-connection: close\r\n'
        elif len(line) > 0:
            return_header += line + '\r\n'

    # final newline
    return_header += '\r\n'

    return return_header, first_line, host_elements[0], int(port)

# this handles a single client
def handle_thread(client_sock, address):
    input_buffer = bytearray()
    while len(input_buffer) < 4 or input_buffer[-4:] != b'\r\n\r\n':
        input_buffer.extend(receive_from_stream(client_sock, 1)) # i know pulling one byte at a time is slow; it works for now though

    # we now have a complete HTTP request header


    header, first_line, host, port = parse_http_request(input_buffer.decode("utf-8"))

    print '>>>', first_line

    if first_line[:3].lower() == 'get':
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((host, port))

        server_sock.send(header)

        while True:
            buf = server_sock.recv(65525)
            if not buf:
                break
            else:
                client_sock.send(buf)

        server_sock.close()
        client_sock.close()

    elif first_line[:7].lower() == 'connect':
        #don't know if this would work
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((host, port))

        client_sock.send(b'HTTP/1.0 200 OK')
        #sending to client then recieving from server and repeating until finished
        while True:
            clientToServer = os.fork()
            if clientToServer == 0:
                bufc = client_sock.recv(65525)
                if not bufc:
                    break
                else:
                    server_sock.send(bufc)
            else:
                bufs = server_sock.recv(65525)
                if not bufs:
                    break
                else:
                    client_sock.send(bufs)
        os.waitpid()
        server_sock.close()
        client_sock.close()
    else:
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((host, port))

        client_sock.send(b'HTTP/1.0 200 OK')

        server_sock.close()
        client_sock.close()



def main():
    sock = socket(AF_INET, SOCK_STREAM)
    port = 12235
    sock.bind(('', port))
    sock.listen(10) # queue up to 10 requests

    print "Proxy listening on port", port

    while True:
        client_sock, client_addr = sock.accept()
        thread.start_new_thread(handle_thread, (client_sock, client_addr))



if __name__ == '__main__':
    main()