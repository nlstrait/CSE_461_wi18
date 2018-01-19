import socket
import binascii


def generate_packet(payload, p_secret, step):

	payload_len = len(payload)
	msg = payload_len.to_bytes(4, byteorder='big')
	msg += p_secret.to_bytes(4, byteorder='big')
	msg += step.to_bytes(2, byteorder='big')

	student_num = 982
	msg += student_num.to_bytes(2, byteorder='big')

	#msg += payload.encode()

	#if payload_len % 4 != 0:
#		to_add = 4 - payload_len % 4
#		msg += bytes(to_add)
#		print("added", to_add)

	return msg


#IP = '0.0.0.0'
IP = '128.208.1.138'  # attu2.cs.washington.edu
#IP = '128.208.1.139'  # attu3.cs.washington.edu
PORT = 12235
MESSAGE = "hello world"

msg_bytes = generate_packet(MESSAGE, p_secret=0, step=1)

print(len(msg_bytes))
print(msg_bytes)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(msg_bytes, (IP, PORT))
print('sent msg')

#data, server = sock.recvfrom(1024)
#print(data)
#print(server)

