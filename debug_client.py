from socket import *
import random
from  struct import *


# this also verifies the length and padding of the packet
def verify_header(message, psecret, step, sid):
    if len(message) < 12:
        print 'length < 12'
        return False

    if len(message) % 4 != 0:
        print 'not padded'
        return False

    payload_len = unpack('!I', message[0:4])[0]
    if len(message) - 12 < payload_len:
        print 'unexpected length'
        return False

    secret = unpack('!I', message[4:8])[0]
    if secret != psecret:
        print 'secret incorrect'
        return False

    step_num = unpack('!H', message[8:10])[0]
    if step_num != step:
        print 'step incorrect'
        return False

    student_id = unpack('!H', message[10:12])[0]
    if student_id != sid:
        print 'sid incorrect'
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

def main():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', 12236))
    port = 12235
    addr = ("127.0.0.1", port)

    message = generate_header(13, 0, 1, 361)
    message.extend(b'hello, world\0\0\0\0') #payload with padding
    sock.sendto(message, addr)

    recvd_packet, server_address = sock.recvfrom(4096)
    if not verify_header(recvd_packet, 0, 2, 361):
        print 'server packet header failed'
        return

    print 'server packet header checked'



if __name__ == '__main__':
    main()