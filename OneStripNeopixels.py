
import time
import board
import neopixel

#Initialise, a strips variable, provide the GPIO Data Pin
# utilized and the amount of LED Nodes on the strip and brightness (0 to 1 value)

pixels1 = neopixel.NeoPixel(board.D18, 300, brightness=1, auto_write=False)
#Also, create an arbitrary count variable

x = 0

pixels1.fill((0, 220, 0))
#LED Node 10 and the color Blue were selected
pixels1[10] = (0, 20, 255)
#Showing a different color
pixels1.show()
time.sleep(4)

#Below will loop until variable x has a value of 35

while x<35:
    pixels1[x] = (255, 0, 0)
    pixels1[x-5] = (255, 0, 100)
    pixels1[x-10] = (0, 0, 255)
    #Add 1 to the counter
    x=x+1
    #Add a small time pause which will translate to 'smoothly' changing color
    pixels1.show()
    time.sleep(0.05)

#Below section is the same process as the above loop, just in reverse

while x>-15:
    pixels1[x] = (255, 0, 0)
    pixels1[x+5] = (255, 0, 100)
    pixels1[x+10] = (0, 255, 0)
    x=x-1
    pixels1.show()
    time.sleep(0.05)

time.sleep(4)

#Complete the script by returning all the LEDs to the off
pixels1.fill((0, 0, 0))
pixels1.show()
