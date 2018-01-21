import socket
import struct
import threading
from time import sleep


IP = '128.208.1.138'  # attu2.cs.washington.edu
#IP = '128.208.1.139'  # attu3.cs.washington.edu
ACK_FLAG = 0

# for threading
#data = None
#server = None


def generate_packet(payload, p_secret, step):

	packet = bytearray()

	# '>' indicates big-endian
	# 'I' indicates 4-byte unsigned int
	# 'H' indicates 2-byte unsigned int
	packet.extend(struct.pack('>I', len(payload)))
	packet.extend(struct.pack('>I', p_secret))
	packet.extend(struct.pack('>H', step))
	packet.extend(struct.pack('>H', 982))
	packet.extend(bytearray(payload))

	padding = '\0' * ((4 - len(payload)) % 4)
	packet.extend(bytearray(padding))

	return packet


def disassemble_packet(packet):

	payload_len = struct.unpack('>I', packet[0:4])[0]
	#p_secret = struct.unpack('>I', packet[4:8])[0]
	#step = struct.unpack('>H', packet[8:10])[0]
	#student_num = struct.unpack('>H', packet[10:12])[0]

	return packet[12:12+payload_len] #, p_secret, step, student_num


def receive_packet(sock, buffer_size=4096):
	data, server = sock.recvfrom(buffer_size)


def main():
	global data, server

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	""" =============== STAGE A =============== """

	print '--- stage A started ---'

	packet = generate_packet('hello world\0', p_secret=0, step=1)

	sock.sendto(packet, (IP, 12235))

	data, server = sock.recvfrom(4096)

	payload = disassemble_packet(data)
	num = struct.unpack('>I', payload[0:4])[0]
	length = struct.unpack('>I', payload[4:8])[0]
	udp_port = struct.unpack('>I', payload[8:12])[0]
	secret_a = struct.unpack('>I', payload[12:16])[0]

	print '       num :', num
	print '       len :', length
	print '  udp_port :', udp_port
	print '  secret_a :', secret_a
	print '--- stage A complete ---\n'


	""" =============== STAGE B =============== """

	print '--- stage B started ---'

	acked_packet_ids = []

	for i in range(0, num):

		payload = struct.pack('>I', i) + length * struct.pack('>I', 0)
		packet = generate_packet(payload, secret_a, step=1)
		print len(packet)

		# start thread that waits for message from server
		data = None
		t = threading.Thread(target=receive_packet, args=[sock])
		t.start()

		while True:
			print 'sending packet', i
			sock.sendto(packet, (IP, udp_port))
			sleep(0.5)

			# if thread is still alive, we're still waiting on the server
			if not t.isAlive():
				t.join()
				break

		# record server's acknowledgement message
		acked_packet_ids.append(struct.unpack('>I', data)[0])

	for apd in acked_packet_ids:
		print apd

	print '--- stage B complete ---\n'


def thread_method():
	sleep(1.0)


def thread_test():
	t = threading.Thread(target=thread_method)
	t.start()

	print t.isAlive()
	sleep(1.0)
	print t.isAlive()



if __name__ == '__main__':
	main()
	#thread_test()

