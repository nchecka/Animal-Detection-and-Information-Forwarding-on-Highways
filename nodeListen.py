import socket
import sys
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ("", 10000)
#print >>sys.stderr, 'starting up on %s port %s' % server_address
sys.stderr.write('\nstarting up on %s port %s' % server_address)
sock.bind(server_address)

while True:
    #print >>sys.stderr, '\nwaiting to receive message'
    sys.stderr.write('\nwaiting to receive message')
    data, address = sock.recvfrom(4096)
    
    #print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    sys.stderr.write('\nreceived %s bytes from %s' % (len(data), address))
    #print >>sys.stderr, data
    sys.stderr.write('\n%s\n' % data)

    GPIO.output(12, 1)
    sleep(0.1) # Time in seconds.
    GPIO.output(12, 0)
    GPIO.output(12, 1)
    sleep(0.1) # Time in seconds.
    GPIO.output(12, 0)
    GPIO.output(12, 1)
    sleep(0.1) # Time in seconds.
    GPIO.output(12, 0)
#    if data:
#        sent = sock.sendto(data, address)
#        print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)