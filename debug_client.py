from socket import *
import random
import struct
from  struct import pack, unpack


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

def main():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', 12236))
    port = 12235
    addr = ("127.0.0.1", port)

    message = generate_header(13, 0, 1, 361)
    message.extend(b'hello, world\0\0\0\0') #payload with padding
    sock.sendto(message, addr)


    '''
    ===============STAGE B================
    '''
    recvd_packet, server_address = sock.recvfrom(4096)
    if not verify_header(recvd_packet, 0, 2, 361):
        print 'server packet header failed'
        return

    print 'server packet header checked'
    payload_len, secret_0, step_num = parse_header(recvd_packet)

    payload = recvd_packet[12:]
    num, length, udp_port, secret_a = unpack('!IIII', payload[:payload_len])
    print unpack('!IIII', payload[:payload_len])

    stage_b_socket = socket(AF_INET, SOCK_DGRAM)
    stage_b_socket.bind(('', udp_port + 1))
    stage_b_addr = ("127.0.0.1", udp_port)

    for packet_id in range(num):
        message = generate_header(length + 4, secret_a, 1, 361)
        message.extend(pack('!I', packet_id))
        for i in range(length): # payload
            message.extend(b'\0')
        while len(message) % 4: # pad
            message.extend(b'\0')

        stage_b_socket.settimeout(1)
        acked = False
        while not acked:
            print 'sending packet ', packet_id
            stage_b_socket.sendto(message, stage_b_addr)
            try:
                recvd_packet, server_address = stage_b_socket.recvfrom(4096)
                if unpack('!I', recvd_packet[12:16])[0] == packet_id:
                    print 'acked'
                    acked = True
            except timeout:
                print 'not acked'
                acked = False

    



if __name__ == '__main__':
    main()