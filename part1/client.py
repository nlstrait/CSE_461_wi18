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
    if len(sys.argv) == 1:
        IP = "attu2.cs.washington.edu"
    elif len(sys.argv) == 2:
        arg1 = sys.argv[1]
        if arg1.lowercase == "local":
            IP = "127.0.0.1"
        elif arg1.lowercase == "remote":
            IP = "attu2.cs.washington.edu"
        else:
            print "unknown argument"
            sys.exit(0)
    else:
        print "too many arguments"
        sys.exit(0)


    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', 12236))
    port = 12235
    addr = (IP, port)

    message = generate_header(12, 0, 1, 361)
    message.extend(b'hello world\0') #payload with padding
    sock.sendto(message, addr)


    '''
    =============== STAGE B ================
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
    stage_b_addr = (IP, udp_port)

    for packet_id in range(num):
        message = generate_header(length + 4, secret_a, 1, 361)
        message.extend(pack('!I', packet_id))
        for i in range(length): # payload
            message.extend(b'\0')
        while len(message) % 4: # pad
            message.extend(b'\0')

        stage_b_socket.settimeout(0.5)
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

    print 'past loop'

    stage_b_socket.settimeout(None)
    recvd_packet, server_address = stage_b_socket.recvfrom(4096)
    if not verify_header(recvd_packet, secret_a, 2, 361):
        print 'server packet header failed'
        return

    payload = recvd_packet[12:]
    tcp_port, secret_b = unpack('!II', payload[:parse_header(recvd_packet)[1]])
    print tcp_port, secret_b

    '''
    =============== STAGE C ================
    '''
    stage_c_socket = socket()
    stage_c_socket.connect((IP, tcp_port))
    recvd_packet = receive_from_stream(stage_c_socket, 28) # expecting a packet padded to 28 bytes
    if not verify_header(recvd_packet, secret_b, 2, 361):
        print 'stage c header failed'
        return

    payload_len, secret_b, step_num = parse_header(recvd_packet)
    if payload_len >= 13: # to account for server bug
        payload_len = 13
    else:
        print 'stage c payload length failed'
        return

    payload = recvd_packet[12:]

    num2, length2, secret_c, char_c = unpack('!IIIc', payload[:payload_len])

    print unpack('!IIIc', payload[:payload_len])



    '''
    =============== STAGE D ================
    '''
    for i in range(num2):
        message = generate_header(length2, secret_c, 1, 361)
        for j in range(length2):
            message.extend(char_c)
        while len(message) % 4:
            message.extend('\0')

        stage_c_socket.send(message)

    packet_d = receive_from_stream(stage_c_socket, 16)
    secret_d = unpack('!I', packet_d[12:16])[0]

    print 'done'
    print 'secret a: ', secret_a
    print 'secret b: ', secret_b
    print 'secret c: ', secret_c
    print 'secret d: ', secret_d




if __name__ == '__main__':
    main()