import socket
import struct


IP = '128.208.1.138'  # attu2.cs.washington.edu
#IP = '128.208.1.139'  # attu3.cs.washington.edu
PORT = 12235
MESSAGE = "hello world"


def generate_packet(payload, p_secret, step):
	payload += '\0'

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


def main():
	packet = generate_packet(MESSAGE, p_secret=0, step=1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(packet, (IP, PORT))
	print 'message sent'

	data, server = sock.recvfrom(4096)
	print(data)


if __name__ == '__main__':
	main()

