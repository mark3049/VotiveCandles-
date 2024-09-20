

class FlickerColor:
    def __init__(self, minColor, maxColor):
        self.map = {}
        array = 'abcdefghijklmnopqrstuvwxyz'
        for i in range(26):
            r = int((maxColor[0]-minColor[0])/25*(i)+minColor[0])
            g = int((maxColor[1]-minColor[1])/25*(i)+minColor[1])
            b = int((maxColor[2]-minColor[2])/25*(i)+minColor[2])
            self.map |= {array[i]: (r, g, b)}
    
    def get(self, index):
        return self.map[index]

if __name__ == "__main__":
    color = FlickerColor((0,0,0), (255,255,255))
    print(color.map)
    print(color.get('a'))
    print(color.get('m'))
    