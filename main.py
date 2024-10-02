#!/usr/bin/python

import time
import logging
import serial
import serial.tools.list_ports
import argparse
import leds
import random
from keyboard import KBHit
from receive import read_serial
from kneeler import WorkThread
from noise import NoiseThread

log = logging.getLogger(__name__)

LED_Width = 5
LED_Height = 6
LightColor = (255,255,255)
NEXT_NOISE = [10, 60] # 下一次Noise時間
NOISE_DURATION_RANGE = [3, 6]
KNEELING_TIME = 5  # 最小跪拜時間 sec
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


def get_next_noise():
    next = random.randint(NEXT_NOISE[0], NEXT_NOISE[1])
    log.debug("next noise incoming in %d", next)
    return time.time() + next


def read_serial_action(port):
    v = read_serial(port)
    if not v:
        return None
    s = [ x for x in v if x > Sensitivity]
    if len(s) > 0: # 任何一個大於Sensitivity
        return "d" # down
    s = [ x for x in v if x < 10]
    if len(s) == len(v): # 全部小於10
        return 'u'


def main(leds, kb, port):
    status = [False for x in range(len(leds))]
    
    kneeler_worker = WorkThread(
        leds, 
        LightColor, 
        status, 
        KNEELING_TIME
        )
    kneeler_worker.start()
    
    noise_worker = NoiseThread(
        leds, 
        LightColor, 
        status, 
        NOISE_DURATION_RANGE
        )
    noise_worker.start()

    is_down = False
    noise_time = get_next_noise()
    while kneeler_worker.is_alive():
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
                if noise_worker.IsOnset(): # 停止噪音動作
                    noise_worker.Ending()
                    time.sleep(0.5)
                kneeler_worker.queue.put('down')
                is_down = True
        elif action == 'u':
            if is_down:
                log.info("up")
                kneeler_worker.queue.put('up')
                is_down = False
        elif action == 's':  # keycode, Debug用
            if is_down:
                continue
            noise_time = time.time() - 1

        if is_down or noise_worker.IsOnset(): # 延後發作
            if time.time() > noise_time:
                noise_time = get_next_noise()
        
        if time.time() > noise_time:
            if noise_worker.IsOnset():
                noise_time = get_next_noise()
            else:
                noise_worker.Onset(random.randint(0, len(leds)))
        time.sleep(1)
    
    kneeler_worker.is_exit = True    
    kneeler_worker.join()
    noise_worker.is_exit = True
    noise_worker.join()


def parser_opt():
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--debug", action="store_true", default=False, help="enable debug mode")
    p.add_argument("-s", "--skip", action="store_true", default=False, help="skip power on led")
    return p.parse_args()

# 
# sudo systemctl stop demo.service
if __name__ == "__main__":
    argc = parser_opt()
    logging.basicConfig(level=logging.DEBUG if argc.debug else logging.INFO)
    log.debug("opt:%s", argc)
    led = leds.LEDs(LED_Width, LED_Height)

    kb = None
    if argc.debug:        
        kb = KBHit()
        log.info("enable keyboard")

    try:
        if not argc.skip:
            show_power_on(led)
        wait_serial_online(led)
        port = serial.Serial('/dev/ttyUSB0',115200)
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
