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
from receive import read_serial

log = logging.getLogger(__name__)

LED_Width = 5
LED_Height = 6
MIN_DOWNTIME = 5  # 最小跪拜時間
LightColor = (255,255,255)
LightStatus = [False for x in range(LED_Width*LED_Height)]
NEXT_NOISE_MIN_TIME = 10
NEXT_NOISE_MAX_TIME = 60
Sensitivity = 85

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
    def __init__(self, leds):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self._leds = led
        self._ready_exit = False
        self._leds.fill((0,0,0))
        self._leds.show()
        self.is_exit = False
    
    def push_down(self):
        pattern = 'abcdefghijklmnopqrstuvwxyzazaaz'
        darks = [ x for x in range(len(self._leds)) if not LightStatus[x]]
        dark_index = random.choice(darks)
        step = MIN_DOWNTIME/len(pattern)/100
        log.info("index:%d from %s (step:%s sec)",dark_index, darks, step)
        fc = flicker.FlickerPattern(pattern=pattern, maxColor=LightColor)

        count = 100
        for x in range(len(pattern)*100):
            if self.is_exit:
                return
            
            if self.queue.qsize() > 0:
                msg = self.queue.get()
                log.info("push_down get msg %s", msg)
                if msg == 'up':
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
        LightStatus[dark_index] = True
        self._leds[dark_index] = LightColor
        self._leds.show()
        log.info("push_down successed")

    def run(self):        
        is_down = False
        while not self.is_exit:
            if self.queue.qsize() > 0:
                msg = self.queue.get()
                log.debug("run get msg:%s", msg)
                if msg == 'down':
                    self.push_down()         
            time.sleep(0.1)
        log.debug("run exit")

class NoiseThread(threading.Thread):
    def __init__(self, leds):
        threading.Thread.__init__(self)
        self._leds = leds
        self._index = -1
        self._flickered = False
        self.is_exit = False

    def shoot(self, index):
        self._index = index
        self._flickered = True
        log.info("shoot %d", index)
    
    def flicker_stop(self):
        self._flickered = False

    def flickered(self):
        return self._flickered
    
    def do_flicker(self):
        index = self._index
        state = LightStatus[index]
        pattern = random.choice(flicker.flickerStrings)
        fc = flicker.FlickerPattern(pattern=pattern, maxColor=LightColor)
        total = random.randint(20, 40) # 2 ~ 4 sec
        count = 0
        log.info("do flicker total:%s, pattern:%s", total, pattern)
        while self._flickered:
            self._leds[index] = fc.next()
            self._leds.show()
            time.sleep(0.1)
            count += 1
            if count > total:
                break
        self._leds[index] = LightColor if state else (0,0,0)
        self._leds.show()
        self._flickered = False
        log.info("do flicker successed")
        
    
    def run(self):
        while not self.is_exit:
            if not self._flickered:
                time.sleep(0.1)
                continue
            self.do_flicker()
        log.debug("noise exit")

def get_next_noise():
    next = random.randint(NEXT_NOISE_MIN_TIME, NEXT_NOISE_MAX_TIME)
    log.debug("next noise incoming in %d", next)
    return time.time() + next

def read_serial_action(port):
    v = read_serial(port)
    if not v:
        return None
    s = [ x for x in v if x > Sensitivity]
    if len(s) > 0: # 任何一個大於90
        return "d" # down
    s = [ x for x in v if x < 10]
    if len(s) == len(v): # 全部小於10
        return 'u'

def main(leds, kb, port):
    worker = WorkThread(leds)
    worker.start()
    noise_worker = NoiseThread(leds)
    noise_worker.start()

    is_down = False
    noise_time = time.time() + random.randint(10, 60)
    while worker.is_alive():
        action = None

        if kb and kb.kbhit():
            key = kb.getch()
            keycode = ord(key)
            if keycode == 27: # ESC
                break;
            else:
                action = key
        
        saction = read_serial_action(port)
        if saction:
            action = saction

        if action == 'd':
            log.info("down")
            if not is_down:
                if noise_worker.flickered():
                    noise_worker.flicker_stop()
                    time.sleep(0.5)
                worker.queue.put('down')
                is_down = True
        elif action == 'u':
            if is_down:
                log.info("up")
                worker.queue.put('up')
                is_down = False
        elif action == 's':
            if is_down:
                continue
            noise_time = time.time() - 1

        if is_down or noise_worker.flickered(): # 延後發作
            if time.time() > noise_time:
                noise_time = get_next_noise()
        
        if time.time() > noise_time:
            if noise_worker.flickered():
                noise_time = get_next_noise()
            else:
                noise_worker.shoot(random.randint(0, len(leds)))
        time.sleep(1)
    
    worker.is_exit = True    
    worker.join()
    noise_worker.is_exit = True
    noise_worker.join()


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
        port = serial.Serial('/dev/ttyUSB0',9600)
        main(led, kb, port)
    except Exception as ex:
        log.exception(ex)
    finally:
        port.close()
        if kb:
            kb.set_normal_term()
        led.clear()
        led.show()
        led.deinit()
