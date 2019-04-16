# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#for the LCD display
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

#for the thermal camera
import os
import subprocess
import math
import time

import busio
import board

import numpy as np
import pygame
from scipy.interpolate import griddata

from colour import Color

import adafruit_amg88xx
#from Adafruit_AMG88xx import Adafruit_AMG88xx

#for sockets
import socket
import sys


#for the motor driver
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT) #pin 36

WIDTH = 128
HEIGHT = 128
SPEED_HZ = 4000000


# Raspberry Pi configuration.
DC = 24 #Pin number 18
RST = 23 #Pin Number 16
SPI_PORT = 0
SPI_DEVICE = 0

# BeagleBone Black configuration.
# DC = 'P9_15'
# RST = 'P9_12'
# SPI_PORT = 1
# SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev( 
        SPI_PORT, #port number
        SPI_DEVICE, #device number
        max_speed_hz=SPEED_HZ))

# Initialize display.
disp.begin()

# Clear the display to a red background.
# Can pass any tuple of red, green, blue values (from 0 to 255 each).
disp.clear((0, 0, 0))
 
# Alternatively can clear to a black screen by calling:
# disp.clear()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

# # Draw some shapes.
# # Draw a blue ellipse with a green outline.
# draw.ellipse((10, 10, 110, 80), outline=(0,255,0), fill=(255,0,0))

# # Draw a purple rectangle with yellow outline.
# #(left, top, right, bottom)
# draw.rectangle((10, 90, 110, 120), outline=(255,255,0), fill=(255,0,255))

# # Draw a white X.
# draw.line((10, 90, 110, 230), fill=(255,255,255))
# draw.line((10, 230, 110, 170), fill=(255,255,255))

# # Draw a cyan triangle with a black outline.
# draw.polygon([(10, 275), (110, 240), (110, 310)], outline=(0,0,0), fill=(0,255,255))

# draw.point((64, 105), fill=(255,0,0))
# draw.point((64, 106), fill=(255,0,0))
# draw.point((64, 107), fill=(255,0,0))
# draw.point((64, 64), fill=(0,255,0))
# # Load default font.
# font = ImageFont.load_default()

# # Alternatively load a TTF font.
# # Some other nice fonts to try: http://www.dafont.com/bitmap.php
# #font = ImageFont.truetype('Minecraftia.ttf', 16)

# # Define a function to create rotated text.  Unfortunately PIL doesn't have good
# # native support for rotated fonts, but this function can be used to make a
# # text image and rotate it so it's easy to paste in the buffer.
# def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
#     # Get rendered font width and height.
#     draw = ImageDraw.Draw(image)
#     width, height = draw.textsize(text, font=font)
#     # Create a new image with transparent background to store the text.
#     textimage = Image.new('RGBA', (width, height), (0,0,0,0))
#     # Render the text.
#     textdraw = ImageDraw.Draw(textimage)
#     textdraw.text((0,0), text, font=font, fill=fill)
#     # Rotate the text image.
#     rotated = textimage.rotate(angle, expand=1)
#     # Paste the text into the image, using it as a mask for transparency.
#     image.paste(rotated, position, rotated)

# # Write two lines of white text on the buffer, rotated 90 degrees counter clockwise.
# draw_rotated_text(disp.buffer, 'Hello World!', (150, 120), 90, font, fill=(255,255,255))
# draw_rotated_text(disp.buffer, 'This is a line of text.', (170, 90), 90, font, fill=(255,255,255))

# # Write buffer to display hardware, must be called to make things visible on the
# # display!
# disp.display()

"""This example is for Raspberry Pi (Linux) only!
   It will not work on microcontrollers running CircuitPython!"""



i2c_bus = busio.I2C(board.SCL, board.SDA)

#low range of the sensor (this will be blue on the screen)
MINTEMP = 26.

#high range of the sensor (this will be red on the screen)
MAXTEMP = 32.

#how many color values we can have
COLORDEPTH = 1024

os.putenv('SDL_FBDEV', '/dev/fb1')
#pygame.init()

#initialize the sensor
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)
#sensor = Adafruit_AMG88xx.AMG88XX(i2c_bus)

# pylint: disable=invalid-slice-index
points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
# pylint: enable=invalid-slice-index

#sensor is an 8x8 grid so lets do a square
height = 128
width = 128

#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

# lcd = pygame.display.set_mode((width, height))

# lcd.fill((255, 0, 0))

# pygame.display.update()
# pygame.mouse.set_visible(False)

# lcd.fill((0, 0, 0))
# pygame.display.update()

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#let the sensor initialize
time.sleep(.1)

# Create a UDP socket
server_address = ('<broadcast>', 10000)
message = 'This is the message.  It will be repeated.'
PWM = 0
time_a = 0
while True:

    #read the pixels
    pixels = []
    for row in sensor.pixels:
        pixels = pixels + row
    pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

    #perform interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
    pixelTotal = 0;
    #draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            #pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)],
            #                  (displayPixelHeight * ix, displayPixelWidth * jx,
            #                   displayPixelHeight, displayPixelWidth))
            #draw.pixel(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)],
            #                 (displayPixelHeight * ix, displayPixelWidth * jx,
            #                  displayPixelHeight, displayPixelWidth))

            #coordinates
            x0 = displayPixelHeight * ix
            y0 = displayPixelWidth * jx
            x1 = x0 + displayPixelHeight 
            y1 = y0 + displayPixelWidth
            draw.rectangle((x0, y0, x1, y1), fill = colors[constrain(int(pixel), 0, COLORDEPTH- 1)]);
            pixelTotal +=pixel

    if(PWM== 0 and (time.time() - time_a) > 3):
        PWM = 1
        GPIO.output(16, 0)
    elif (PWM == 1 and (time.time() - time_a) > 3):
        PWM = 0
        GPIO.output(16,1)
    stri = "Pixel Total: " + str(pixelTotal/255) + "\n"
    disp.display()
    #print (stri)

    if(pixelTotal > -2000):
        detInd = "Detected"
        print ("Detected")
        GPIO.output(16, 0)
        #sleep(1) # Time in seconds.
        limit = 0
        #while limit < 30 :
        time_a = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:

            # Send data
            #print >>sys.stderr, 'sending "%s"' % message
            sys.stderr.write('sending "%s"' % detInd)
            sent = sock.sendto(detInd.encode('utf-8'), server_address)

            # Receive response
        #    print >>sys.stderr, 'waiting to receive'
        #    data, server = sock.recvfrom(4096)
        #    print >>sys.stderr, 'received "%s"' % data

        finally:
            #print >>sys.stderr, 'closing socket'
            sys.stderr.write("\nclosing socket\n")

            sock.close()
    else:
        time_a = 0
    #subprocess.call("echo Hello World", shell=True)
    #subprocess.call("echo '1' | netcat -u 192.168.43.53 9099 -q 0", shell=True)

    # = sock.recvfrom(1024) # buffer size is 1024 bytes
    #print ("received message:", data)

    #subprocess.call("^D", shell=True)
    #subprocess.run(["netcat ","192.168.43.53","9099", "<", "something.txt"]) 
    #os.system('hello')
    #os.system('netcat 192.168.43.53 9099 < something.txt -l')
    #pygame.display.update()
