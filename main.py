import time
import logging
import serial
import serial.tools.list_ports
import argparse
import leds
import threading
import queue
import random
import flicker
from keyboard import KBHit

log = logging.getLogger(__name__)

LED_Width = 5
LED_Height = 6
MIN_DOWNTIME = 5  # 最小跪拜時間
LightColor = (255,255,255)

def show_power_on(led):

    log.info("begin show power on screen")
    
    # up to down
    for y in range(led.height()):
        led.clear()
        for level in range(0,256,8):
            for x in range(led.width()):
                led.setXY(x, y, (level, level, level))
            led.show()
            time.sleep(0.02)
    # left to right
    for x in range(led.width()):
        led.clear()
        for level in range(0, 256, 8):
            for y in range(led.height()):
                led.setXY(x, y, (level, level, level))
            led.show()
            time.sleep(0.02)


def serial_port_exist():
    for p in list(serial.tools.list_ports.comports()):
        if "ttyUSB0" in p.device:
            log.info("serail port exist %s", p)
            return True
    log.debug("not exist")
    return False


def wait_serial_online(led):
    while not serial_port_exist():
        led.fill((64,0,0))
        led.show()
        time.sleep(1)
        led.fill((0,0,0))
        led.show()
        time.sleep(1)

class WorkThread(threading.Thread):
    def __init__(self, leds, queue):
        threading.Thread.__init__(self)
        self._queue = queue
        self._leds = led
        self._ready_exit = False
        self._light = [False for x in range(len(leds))]
        self._leds.fill((0,0,0))
        self._leds.show()
    
    def push_down(self):
        pattern = 'abcdefghijklmnopqrstuvwxyzazaaz'
        darks = [ x for x in range(len(self._light)) if not self._light[x]]
        dark_index = random.choice(darks)
        step = MIN_DOWNTIME/len(pattern)/100
        log.info("index:%d from %s (step:%s sec)",dark_index, darks, step)
        fc = flicker.FlickerPattern(pattern=pattern, maxColor=LightColor)

        count = 100
        for x in range(len(pattern)*100):
            if self._queue.qsize() > 0:
                msg = self._queue.get()
                log.info("push_down get msg %s", msg)
                self._leds[dark_index] = (0, 0, 0)
                self._leds.show()
                log.info("push_down cancel")
                return;
        
            if count >= 100:
                color = fc.next()
                self._leds[dark_index] = color
                self._leds.show()
                log.debug("index:%d color:%s", dark_index, color)
                count = 0
            else:
                count += 1
            time.sleep(step)
        self._light[dark_index] = True
        self._leds[dark_index] = LightColor
        self._leds.show()
        log.info("push_down successed")

    def run(self):        
        is_down = False
        while True:
            if self._queue.qsize() > 0:
                msg = self._queue.get()
                log.debug("run get msg:%s", msg)
                if msg == 'exit':
                    break;
                elif msg == 'down':
                    self.push_down()         
            time.sleep(0.1)

def main(led, kb):
    my_queue = queue.Queue()
    worker = WorkThread(led, my_queue)
    worker.start()
    time.sleep(1)
    while worker.is_alive():
        if kb and kb.kbhit():
            key = kb.getch()
            keycode = ord(key)
            if keycode == 27: # ESC
                log.info("exit")
                my_queue.put('up')
                my_queue.put('exit')
                break;
            elif key == 'd':
                log.info("down")
                my_queue.put('down')
            elif key == 'u':
                log.info("up")
                my_queue.put('up')
    worker.join()


def parser_opt():
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--debug", action="store_true", default=False, help="enable debug mode")
    p.add_argument("-s", "--skip", action="store_true", default=False, help="skip power on led")
    return p.parse_args()


if __name__ == "__main__":
    argc = parser_opt()
    logging.basicConfig(level=logging.DEBUG if argc.debug else logging.INFO)
    log.debug("opt:%s", argc)
    led = leds.LEDs(LED_Width, LED_Height)

    kb = None
    if argc.debug:
        kb = KBHit()

    try:
        if not argc.skip:
            show_power_on(led)
        wait_serial_online(led)
        main(led, kb)
    except Exception as ex:
        log.exception(ex)
    finally:
        if kb:
            kb.set_normal_term()
        led.clear()
        led.show()
        led.deinit()
