import board
import neopixel
import logging
import time
import random
from collections.abc import Sequence

log = logging.getLogger(__name__)

class LEDs(neopixel.NeoPixel):
    black_color = (0,0,0)
    def __init__(self, width, height):
        self._width = width
        self._height = height
        super().__init__(board.D18, 
            width * height, 
            brightness=1, auto_write=False)
        self.fill(LEDs.black_color)
    
    def setXY(self, x, y, color):
        self[y*self._width + x] = color
    
    def clear(self):
        self.fill(LEDs.black_color)
        self.show()
    
    def width(self):
        return self._width
    
    def height(self):
        return self._height
    

def _test_meteor(led, color):
    for index in range(30):
        led[index] = color
        led.show()
        time.sleep(1/15)

def _test_random(led):
    while True:
        index = random.randrange(0,30)
        led.clear()
        led[index] = (127,127,127)
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
        print('total led:', len(led))
        _test_run(led)
        _test_random(led)
    except Exception as e:
        print("except:", e)
    finally:
        led.clear()
        led.show()
        led.deinit()
    
        