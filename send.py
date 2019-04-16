import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server_address = ('<broadcast>', 10000)
message = 'This is the message.  It will be repeated.'

try:

    # Send data
    #print >>sys.stderr, 'sending "%s"' % message
    sys.stderr.write('sending "%s"' % message)
    sent = sock.sendto(message.encode('utf-8'), server_address)

    # Receive response
#    print >>sys.stderr, 'waiting to receive'
#    data, server = sock.recvfrom(4096)
#    print >>sys.stderr, 'received "%s"' % data

finally:
	#print >>sys.stderr, 'closing socket'
	sys.stderr.write("\nclosing socket\n")
	sock.close()
