import json
import os

''' example json file:
{"frame": [
{"x": 0, "y": 0, "t": 18.2}, 
{"x": 1, "y": 0, "t": 18.1}, ...

example greyscale PGM image format, V={0-255} for {black-white}:
Here is an example of a small graymap in this format:

P2
# feep.pgm
32 24  # W H
20     # max-val
0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
# max 70 chars/line; 0=black 20=white (max-val)
0  3  3  3  3  0  0  7  7  7  7  0  0 11 11 11 11  0  0 15 15 15 15  0
0  3  0  0  0  0  0  7  0  0  0  0  0 11  0  0  0  0  0 15  0  0 15  0

'''

class Pbm:
    'Support for Portable Bit Map, like PGM for greyscale, PPM for color'

    scene = '' # base for input and output file names
    WIDTH  = 32 # constant for RPi IR cam
    HEIGHT = 24 # constant for RPi IR cam
    min = 0
    max = 0
    t_pixels = []

    def __init__(self, scene_name):
        self.scene = scene_name
        return

    def json_read(self):
        'convert from json data to array of temperature celsius t_pixels'
        print(f'pbm: working dir: {os.getcwd()}', flush=True)
        #return
        fs = open(f'{self.scene}.json', mode='r')
        j = json.load(fs)
        self.min = j['min']
        self.max = j['max']                  
        pixels = j['frame']
        self.t_pixels = []
        for p in pixels:
            x = p['x'] #not used
            y = p['y'] #not used
            t = p['t']
            #print(f'x={x}, y={y}, t={t}')
            self.t_pixels.append(t)
        return

    def histogram_scaling(self, t):
        'convert from temp value to bin nr, 0 .. n-1'
        # todo
        return t

    def make_header(self, magicnumber, maxval, z):
        'return the PBM header part, magic nr is P1, P2, etc'
        s = f'''{magicnumber}
# pbm format written by Pbm.py
{self.WIDTH * z} {self.HEIGHT * z}
{maxval}
'''
        return s

    def float_to_int(self, f):
        'scale f to min/max and return as int 0..255'
        k = (self.max - self.min)/256
        i = int((f - self.min) / k)
        if i < 0 or i >= 256:
            raise ValueError(f'bug with min={self.min}, max={self.max}, f={f}, k={k}, i = {i}')
        return i

    def make_pgm(self):
        'create pgm and write to file, return nr of bytes written'
        #MAX_GREY_VAL = 20 # nr of histogram bins
        Z = 20 # nr PBM pixels for each IR pixel, both horz and vert
        pgm = self.make_header('P5', int(self.max) - int(self.min), Z)
        f = open(f'{self.scene}.pgm', mode='wb')
        f.write(bytes(pgm, encoding='utf8'))
        #line = ''
        #for pixel in self.t_pixels:
        a = [0 for i in range(0, self.WIDTH * Z)]
        for y in range(self.HEIGHT):
            # fill p array with one row of pixel values
            for x in range(self.WIDTH):
                t = self.t_pixels[x + y * self.WIDTH]
                for xz in range(Z):
                    a[xz + x * Z] = self.float_to_int(t)
            # write the p array as bytes to pgm output
            p = bytes(a)
            for yz in range(Z):
                f.write(p)
        f.close()
        nr_of_bytes = len(pgm) + self.HEIGHT * self.WIDTH * Z * Z
        return nr_of_bytes

if __name__ == "__main__":
    'demo of this class'
    scene = 'testphotos/candle_tea'
    print(f'Demo of the Pbm class, scene: {scene}')
    pbm = Pbm(scene)
    pbm.json_read()
    pbm.make_pgm()
    print('done')    
