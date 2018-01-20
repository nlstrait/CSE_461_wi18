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
    secret_a = random.randint(1,1000)

    outgoing_packet = generate_header(16, 0, 2, 361)
    outgoing_packet.extend(pack('!IIII', num, length, udp_port, secret_a))

    sock.sendto(outgoing_packet, address)


    '''
    ===============STAGE B================
    '''
    stage_b_socket = socket(AF_INET, SOCK_DGRAM)
    stage_b_socket.bind(('', udp_port))

    num_acked = 0 # the number of packets acked so far
    while num_acked != num:
        print 'loop'
        packet_b, addr_b = stage_b_socket.recvfrom(4096)

        # drop if packet is malformed
        if not verify_header(packet_b, secret_a, 1, 361):
            return

        payload_len, secret, step_num = parse_header(packet_b)
        if payload_len != length + 4:
            return


        payload = packet_b[12:]
        packet_id = unpack('!I', payload[0:4])[0]
        if packet_id != num_acked: # packets must be received in order; wait for the next packet
            continue



        for byte in payload[4:length]:
            if byte != '\0': # packet payload must be all zero bytes; if not, drop connection
                return

        # all's well; now decide whether to skip the ack step
        if random.randint(0,1):
            continue

        outgoing_packet = generate_header(4, secret_a, 1, 361)
        outgoing_packet.extend(pack('!I', num_acked))
        stage_b_socket.sendto(outgoing_packet, addr_b)
        num_acked += 1

    print 'past loop'
    # got all the packets, now for step b2
    tcp_port = random.randint(49152, 65535) # stick to the dynamic ports
    secret_b = random.randint(1,1000)

    outgoing_packet = generate_header(8, secret_a, 2, 361)
    outgoing_packet.extend(pack('!II', tcp_port, secret_b))
    stage_b_socket.sendto(outgoing_packet, address)

    '''
    ===============STAGE C================
    '''

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