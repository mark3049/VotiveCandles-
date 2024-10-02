import logging
import threading
import random
import flicker
import time

log = logging.getLogger(__name__)

class NoiseThread(threading.Thread):
    def __init__(self, leds, lightcolor, states, duration = [2,4]):
        threading.Thread.__init__(self)
        self._leds = leds 
        self._lightcolor = lightcolor # 燈光顏色
        self._states = states  # LED 明滅狀態
        self._duration = [duration[0]*10, duration[1]*10] # units: 0.1 sec
        self._index = -1
        self._flickering = False
        self.is_exit = False


    def Onset(self, index):
        '''開始發作'''
        self._index = index
        self._flickering = True
        log.info("shoot %d", index)
    
    def Ending(self):
        '''停止發作'''
        self._flickering = False

    def IsOnset(self):
        ''' 是否正在發作'''
        return self._flickering
    
    def do_flicker(self):
        index = self._index
        state = self._states[index]
        pattern = random.choice(flicker.flickerStrings)
        fc = flicker.FlickerPattern(pattern=pattern, maxColor=self._lightcolor)
        total_sec = random.randint(self._duration[0],self._duration[1]) 
        count = 0
        log.info("do flicker total:%s sec, pattern:%s", total_sec/10, pattern)
        while self.IsOnset():
            self._leds[index] = fc.next()
            self._leds.show()
            time.sleep(0.1)
            count += 1
            if count > total_sec:
                break
        
        self._leds[index] = self._lightcolor if state else (0,0,0)  # 復原燈號
        self._leds.show()
        self.Ending()
        log.info("do flicker successed")
        
    
    def run(self):
        while not self.is_exit:
            if not self.IsOnset():
                time.sleep(0.1)
                continue
            self.do_flicker()
        log.debug("noise exit")
