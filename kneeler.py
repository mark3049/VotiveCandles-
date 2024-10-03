import threading
import logging
import queue
import random
import flicker
import time

log = logging.getLogger(__name__)

class WorkThread(threading.Thread):
    def __init__(self, leds, lightcolor, states, confirm_pattern, kneel_time = 5):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self._leds = leds
        self._lightcolor = lightcolor
        self._status = states
        self._brightening_pattern = 'abcdefghijklmnopqrstuvwxyz'
        self._confirm_pattern = confirm_pattern
        self._kneel_time = kneel_time
        self._ready_exit = False
        self._leds.fill((0,0,0))
        self._leds.show()
        self.is_exit = False
        self._is_down_case = False
    
    def IsDown(self):
        return self._is_down_case;

    def push_down(self):
        darks = [ x for x in range(len(self._leds)) if not self._status[x]]
        if len(darks) == 0:
            log.info("all led is active")
            return
        dark_index = random.choice(darks)
        step = self._kneel_time/len(self._brightening_pattern)/100
        log.info("index:%d from %s",dark_index, darks)
        fc = flicker.FlickerPattern(pattern=self._brightening_pattern, maxColor=self._lightcolor)

        count = 100
        for x in range(len(self._brightening_pattern)*100):
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
                #log.debug("index:%d color:%s", dark_index, color)
                count = 0
            else:
                count += 1
            time.sleep(step)
        
        # show confirm pattern in sec
        fc = flicker.FlickerPattern(pattern=self._confirm_pattern, maxColor=self._lightcolor)
        for x in range(len(self._confirm_pattern)):
            self._leds[dark_index] = fc.next()
            self._leds.show()
            time.sleep(0.03)

        self._status[dark_index] = True
        self._leds[dark_index] = self._lightcolor
        self._leds.show()
        log.info("push_down successed")

    def run(self):        
        is_down = False
        while not self.is_exit:
            if self.queue.qsize() > 0:
                msg = self.queue.get()
                log.debug("run get msg:%s", msg)
                if msg == 'down':
                    self._is_down_case = True
                    self.push_down()
                    self._is_down_case = False
            time.sleep(0.1)
        log.debug("run exit")
