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
LightColor = (255,66,0)
NoiseLightColor = (255, 248, 0)
NEXT_NOISE = [15, 30] # 下一次Noise時間
NEXT_NOISE_UP_EVENT = [5, 10] # 起來後,下一次Noise時間
NOISE_DURATION_RANGE = [1, 3]
MIN_KNEELING_TIME = 5  # 最小跪拜時間 sec
MAX_KNEELING_TIME = 2*60 # 最大跪拜時間 sec, 重置所有燈號
min_sensor_value = 85 # 壓力下限 超過就判定為跪下事件 Down event 
noise_pattern = 'madaedagahiaqabaacadaeidfgaaahaiaqbaqanaoqnbqnqnomnaadfao'
kneeler_confirm_pattern = 'madaedagahiaqabaacadaeid'
noise_amount = max(1, LED_Width*LED_Height*5/100)  # Noise 多顆同時

# 全亮後 30min 後自動熄滅60％ 1min turn off 1 led
# 


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


def get_noise_time(offset=0):
    next = random.randint(NEXT_NOISE[0], NEXT_NOISE[1])
    return time.time() + next + offset

def get_up_event_noise_time(offset = 0):
    next = random.randint(NEXT_NOISE_UP_EVENT[0], NEXT_NOISE_UP_EVENT[1])
    return time.time() + next + offset


def read_serial_action(port):
    v = read_serial(port)
    if not v:
        return None
    s = [ x for x in v if x > min_sensor_value]
    if len(s) > 0: # 任何一個大於Sensitivity
        return "d" # down
    s = [ x for x in v if x < 10]
    if len(s) == len(v): # 全部小於10
        return 'u'


class main_worker:
    def __init__(self, leds, kb, port):
        self.leds = leds
        self.kb = kb
        self.port = port
        self.led_status = [False for x in range(len(leds))] # 所有燈的狀態
        self.is_down = False
        self.noise_time = None
        
        self.kneeler_worker = WorkThread(
            leds, 
            LightColor, 
            self.led_status,
            kneeler_confirm_pattern, 
            MIN_KNEELING_TIME
        )
        self.noise_worker = NoiseThread(
            leds, 
            NoiseLightColor, 
            self.led_status,
            noise_pattern,
            NOISE_DURATION_RANGE
            )
    
    def get_action(self):
        action = None

        if self.kb and self.kb.kbhit():
            key = self.kb.getch()
            keycode = ord(key)
            if keycode == 27: # ESC
                action = 'ESC'
            else:
                action = key
            return action
        return read_serial_action(self.port)
    
    def run_down_action(self):
        log.info("down")
        if self.noise_worker.IsOnset(): # 停止噪音動作
            self.noise_worker.Ending()
            time.sleep(0.5)
        self.kneeler_worker.queue.put('down')
        self.is_down = True
    
    def run_up_action(self):
        log.info("up")
        self.kneeler_worker.queue.put('up')
        self.is_down = False
        self.noise_time = get_up_event_noise_time()        
    
    def run_noise_shoot(self):
        log.info("turn on noise immediately")
        self.noise_time = time.time() - 1

    def run_actions(self, action):
        if action == 'd':
            if not self.is_down:
                self.run_down_action()
        elif action == 'u':
            if self.is_down: 
                self.run_up_action()
        elif action == 's':  # keycode, Debug用
            if not self.is_down:
                self.run_noise_shoot()

    def check_noise_action(self):
        if self.noise_worker.IsOnset():
            return

        if self.is_down:
            return
                
        if time.time() > self.noise_time:
            samples = random.sample(range(len(self.leds)), noise_amount)
            duration = self.noise_worker.Onset(samples)
            self.noise_time = get_noise_time(duration)
            log.info("noise planning to %s", (int)(self.noise_time-time.time()))
        else:
            # log.debug("noise count down:%d", (int)(self.noise_time-time.time()))
            pass

    def run(self):
        self.kneeler_worker.start()
        self.noise_worker.start()
        self.is_down = False
        self.noise_time = get_noise_time()
        
        while self.kneeler_worker.is_alive():
            action = self.get_action()
            if action == 'ESC':
                break;            
            self.run_actions(action)

            if not self.is_down:
                self.check_noise_action()
            time.sleep(0.1)
        
        self.kneeler_worker.is_exit = True    
        self.kneeler_worker.join()
        self.noise_worker.is_exit = True
        self.noise_worker.join()


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
        main = main_worker(led, kb, port)
        main.run()
    except Exception as ex:
        log.exception(ex)
    finally:
        port.close()
        if kb:
            kb.set_normal_term()
        led.clear()
        led.show()
        led.deinit()
