from socket import *               # Import socket module
import threading
import random
from  struct import *

# this also verifies the length and padding of the packet
def verify_header(message, psecret, step, sid):
    message_bytes = bytearray(message)
    if len(message) < 12:
        return False

    if len(message) % 4 != 0:
        return False

    payload_len = unpack('!I', message_bytes[0:4])[0]
    if len(message) - 12 < payload_len:
        return False

    secret = unpack('!I', message_bytes[4:8])[0]
    if secret != psecret:
        return False

    step_num = unpack('!I', message_bytes[8:10])[0]
    if step_num != step:
        return False

    student_id = unpack('!I', message_bytes[10:12])[0]
    if student_id != sid:
        return False

    return True


# this extracts the payload length, secret, and step number, and returns them in that order
def parse_header(message):
    return unpack('!I', message_bytes[0:4]), unpack('!I', message_bytes[4:8]), unpack('!H', message_bytes[8:10])


# this handles a single client
def handle_thread(sock, message, address):
    # we've got a new connection

    # drop connection if header is malformed
    if not verify_header(message, 0, 1, 361):
        return


    '''
    ===============STAGE A================
    '''
    payload_len, secret, step_num = parse_header(message)
    if payload_len != 12: # 'hello, world' has length 12 including the null terminator
        return

    payload = message[12:]

    if payload[:payload_len].decode("utf-8") != 'hello, world\0': # python strings aren't null-terminated, but they are in our protocol
        return

    num = random.randint(1,20)
    length = random.randint(1,20)
    udp_port = random.randint(49152, 65535) # stick to the dynamic ports
    secret_a = random.randint(1,100)

    new_message = bytearray()
    # TODO: construct header (and do the rest of it)


    return

def main():
    sock = socket(AF_INET, SOCK_DGRAM)         # Create a socket object
    port = 12235                # Reserve a port for your service.
    sock.bind(('', port))        # Bind to the port

    while True:
        message, address = sock.recvfrom(4096)     # Establish connection with client.
        print 'Got connection from', addr
        threading.start_new_thread(handle_thread, (sock, message, address))



if __name__ == '__main__':
    main()