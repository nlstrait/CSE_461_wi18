from socket import *               # Import socket module
import thread
import random
from  struct import *

# this also verifies the length and padding of the packet
def verify_header(message, psecret, step, sid):
    if len(message) < 12:
        return False

    if len(message) % 4 != 0:
        return False

    payload_len = unpack('!I', message[0:4])[0]
    if len(message) - 12 < payload_len:
        return False

    secret = unpack('!I', message[4:8])[0]
    if secret != psecret:
        return False

    step_num = unpack('!H', message[8:10])[0]
    if step_num != step:
        return False

    student_id = unpack('!H', message[10:12])[0]
    if student_id != sid:
        return False

    print 'header verified'

    return True


# this extracts the payload length, secret, and step number, and returns them in that order
def parse_header(message):
    return unpack('!I', message[0:4])[0], unpack('!I', message[4:8])[0], unpack('!H', message[8:10])[0]


# helper function to generate a new packet header
def generate_header(payload_len, secret, step_num, sid):
    header = bytearray()
    header.extend(pack('!I', payload_len))
    header.extend(pack('!I', secret))
    header.extend(pack('!H', step_num))
    header.extend(pack('!H', sid))
    return header


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
    print payload_len, secret, step_num
    if payload_len != 13: # 'hello, world' has length 13 including the null terminator
        return

    payload = message[12:]

    if payload[:payload_len].decode("utf-8") != 'hello, world\0': # python strings aren't null-terminated, but they are in our protocol
        return

    print 'payload checked'

    num = random.randint(1,20)
    length = random.randint(1,20)
    udp_port = random.randint(49152, 65535) # stick to the dynamic ports
    secret_a = random.randint(1,100)

    new_message = generate_header(16, 0, 2, 361)
    new_message.extend(pack('!I', num))
    new_message.extend(pack('!I', length))
    new_message.extend(pack('!I', udp_port))
    new_message.extend(pack('!I', secret_a))

    sock.sendto(new_message, address)

    '''
    ===============STAGE B================
    '''

    new_socket = socket(AF_INET, SOCK_DGRAM)
    new_socket.bind(('', udp_port))


    return

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