import socket               # Import socket module
import threading

def handle_thread(sock, message, address)
    # flesh this out

def main():
    sock = socket.socket(AF_INET, SOCK_DGRAM)         # Create a socket object
    port = 12235                # Reserve a port for your service.
    sock.bind(('', port))        # Bind to the port

    while True:
        message, address = sock.recvfrom(1024)     # Establish connection with client.
        print 'Got connection from', addr
        threading.start_new_thread(handle_thread, (sock, message, address))



if __name__ == '__main__':
    main()