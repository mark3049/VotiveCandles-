from leds import LEDs
from keyboard import KBHit
import time

# 燈光閃爍特效 a:最低, z:最高, m:預設
flickerStrings = [
    'm', # 0 normal
    'mmnmmommommnonmmonqnmmo', # 1 FLICKER (first variety)
    'abcdefghijklmnopqrstuvwxyzyxwvutsrqponmlkjihgfedcba', # 2 SLOW STRONG PULSE
    'mmmmmaaaaammmmmaaaaaabcdefgabcdefg', # 3 CANDLE (first variety)
    'mamamamamama', # 4 FAST STROBE
    'jklmnopqrstuvwxyzyxwvutsrqponmlkj', # 5 GENTLE PULSE 1
    'nmonqnmomnmomomno', # 6 FLICKER (second variety)
    'mmmaaaabcdefgmmmmaaaammmaamm', # 7 CANDLE (second variety)
    'mmmaaammmaaammmabcdefaaaammmmabcdefmmmaaaa', # 8 CANDLE (third variety)
    'aaaaaaaazzzzzzzz', # 9 SLOW STROBE (fourth variety)
    'mmamammmmammamamaaamammma', # 10 FLUORESCENT FLICKER
    'abcdefghijklmnopqrrqponmlkjihgfedcba', # 11 SLOW PULSE NOT FADE TO BLACK
    'madaedagahiaqabaacadaeidfgaaahaiaqbaqanaoqnbqnqnomnaadfao',
]

class FlickerColor:
    def __init__(self, minColor = (0,0,0), maxColor = (255,255,255)):
        self.map = {}
        array = 'abcdefghijklmnopqrstuvwxyz'
        for i in range(26):
            r = int((maxColor[0]-minColor[0])/25*(i)+minColor[0])
            g = int((maxColor[1]-minColor[1])/25*(i)+minColor[1])
            b = int((maxColor[2]-minColor[2])/25*(i)+minColor[2])
            self.map |= {array[i]: (r, g, b)}
    
    def get(self, index):
        return self.map[index]

class FlickerPattern:
    def __init__(self, pattern, minColor = (0,0,0), maxColor = (255,255,255)):
        self._map = FlickerColor(minColor, maxColor)
        self._pattern = pattern
        self._index = 0
        self._len = len(pattern)
    
    def begin(self, index):
        self._index = index % self._len
    
    def next(self):
        c = self._pattern[self._index]
        self._index = self._index+1 if self._index < self._len -1 else 0
        return self._map.get(c)
    def __str__(self):
        return self._pattern


if __name__ == "__main__":
    leds = LEDs(5, 6)
    fc = FlickerColor((0,0,0), (255,255,255))
    kb = KBHit()
    leds.clear()
    select = 11
    v = FlickerPattern(flickerStrings[select])
    index = 0
    
    try:
        while True:
            if kb.kbhit():
                c = kb.getch()
                c_ord = ord(c)
                if c_ord == 27: # ESC
                   break
                elif c == 'w':
                   select -= 1
                   if select < 0:
                       select = 0
                elif c == 's':
                    select += 1
                    if select >= len(flickerStrings):
                        select = len(flickerStrings) - 1
                else:
                    print('key:', c, 'keycode:', c_ord)
                    continue

                v = FlickerPattern(flickerStrings[select])
                index = 0
                print('key:',c, 'index:', select, 'pattern:', v)
            leds.fill(v.next())
            leds.show()
            time.sleep(0.1)
    finally:
        leds.clear()
        leds.show()
        leds.deinit()
        kb.set_normal_term()
    