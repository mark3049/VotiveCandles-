import logging
import threading
import random
import flicker
import time

log = logging.getLogger(__name__)

time_resolution = 0.05

class NoiseThread(threading.Thread):
    def __init__(self, leds, lightcolor, states, pattern, duration = [2,4]):
        threading.Thread.__init__(self)
        self._leds = leds 
        self._lightcolor = lightcolor # 燈光顏色
        self._states = states  # LED 明滅狀態
        self._pattern = pattern
        self._duration = duration # units: sec        
        self._flickering = False        
        self.is_exit = False


    def Onset(self, indexs):
        '''開始發作'''
        self._indexs = indexs
        self._flickering = True
        self._total_sec = random.randint(self._duration[0], self._duration[1]) 
        log.info("shoot index:%s sec:%s", str(indexs), self._total_sec)
        return self._total_sec
    
    def Ending(self):
        '''停止發作'''
        self._flickering = False

    def IsOnset(self):
        ''' 是否正在發作'''
        return self._flickering
    
    def do_flicker(self):
        size = len(self._indexs)
        fcs = []
        colors = []  # backup color
        for x in range(size):
            fc = flicker.FlickerPattern(pattern=self._pattern, maxColor=self._lightcolor)
            fc.begin(random.randint(0,100))
            fcs.append(fc)
            colors.append(self._leds[self._indexs[x]])
        
        count = 0
        log.info("do flicker total:%s sec, pattern:%s", self._total_sec, self._pattern)
        ticks = self._total_sec / time_resolution
        while self.IsOnset():
            for x in range(size):
                self._leds[self._indexs[x]] = fcs[x].next()
            self._leds.show()
            time.sleep(time_resolution)
            count += 1
            if count > ticks:
                break
        
        for x in range(len(self._indexs)):
            self._leds[self._indexs[x]] = colors[x]  # 復原燈號
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
