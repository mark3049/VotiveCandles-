import board
import neopixel
import logging
import time
import random

log = logging.getLogger(__name__)

class LEDs:
    black_color = (0,0,0)
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = neopixel.NeoPixel(
            board.D18, 
            width * height, 
            brightness=1, auto_write=False)
        self.pixels.fill(LEDs.black_color)
    
    def setXY(self, x, y, color):
        self.pixels[y*self.width + x] = color

    def setIndex(self, index, color):
        self.pixels[index] = color
    
    def fill(self, color):
        self.pixels.fill(color)

    def show(self):
        self.pixels.show()

    def clear(self):
        self.pixels.fill(LEDs.black_color)
        self.show()

class LEDs_Dummy:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def setXY(self, x, y, color):
        pass
    def setIndex(self, index, color):
        pass
    def fill(self, color):
        pass
    def show(self):
        pass
    def clear(self):
        pass

def _test_meteor(led, color):
    for index in range(30):
        led.setIndex(index, color)
        led.show()
        time.sleep(1/15)

def _test_random(led):
    while True:
        index = random.randrange(0,30)
        led.clear()
        led.setIndex(index, (127,127,127))
        led.show()
        time.sleep(1/30)

def _test_run(led):
    _test_meteor(led, (255,0,0))
    led.clear()

    _test_meteor(led, (0,255,0))
    led.clear()

    _test_meteor(led, (0,0,255))
    led.clear()

    _test_meteor(led, (127, 127, 127))
    led.clear()


if __name__ == "__main__":
    led = LEDs(5, 6)
    try:
        _test_run(led)
        _test_random(led)
    except:
        led.clear()
        led.show()
    
        