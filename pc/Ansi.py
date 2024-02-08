'''
Ansi.py
Purpose: read the ansi.txt file and create the log.json if missing.
Usage: needed in case the json is missing. This happens because the camera app
has a bug that raises an exception for negative temperature values.
The ANSI file is still made, but the JSON file will be missing.

example file: captures/20240206_bakpan/20240206_191906/ansi.txt
    skipping 27 lines with 8-bit ANSI characters:
Numeric output
     x= 0 x= 1 x= 2 x= 3 x= 4 x= 5 x= 6 x= 7 x= 8 x= 9 x=10 x=11 x=12 x=13 x=14 x=15 x=16 x=17 x=18 x=19 x=20 x=21 x=22 x=23 x=24 x=25 x=26 x=27 x=28 x=29 x=30 x=31 
y= 0 17.2 17.4 17.5 17.4 17.1 17.0 17.2 17.6 17.4 17.5 17.1 17.5 16.9 17.0 17.1 17.4 16.9 17.0 16.3 16.5 15.5 15.6 15.2 15.5 14.7 14.9 15.9 16.7 16.8 16.8 16.8 17.3 
y= 1 16.8 16.9 17.0 17.2 17.4 17.2 17.4 17.0 17.0 17.4 17.5 16.9 17.0 16.9 17.3 17.0 16.9 16.8 16.7 16.3 15.4 15.6 15.1 15.3 15.4 15.5 16.3 16.7 16.7 16.7 16.9 17.3 
y= 2 16.9 16.7 17.4 17.4 17.0 17.2 17.3 17.8 17.2 17.0 17.4 17.4 16.9 17.2 16.9 17.2 16.5 17.0 16.0 16.0 14.9 14.3 14.2 14.5 14.8 15.0 15.8 16.5 16.5 16.4 16.9 17.1 
y= 3 16.7 16.4 17.2 17.0 17.2 16.8 17.3 17.6 17.1 17.1 17.2 17.2 17.1 17.0 16.8 16.8 16.9 16.3 16.1 15.5 14.1 12.8 12.7 13.1 14.3 14.6 15.0 16.1 16.3 16.9 16.7 17.1 
y= 4 17.2 17.1 17.5 17.2 17.6 17.1 18.0 18.0 17.9 17.9 17.6 17.6 16.9 17.1 16.7 17.2 16.3 16.2 13.6 9.0 4.0 0.9 1.2 4.0 9.0 9.6 13.4 14.5 15.6 15.9 16.7 17.1 
y= 5 17.4 16.7 17.5 17.4 17.4 17.3 18.0 18.0 17.8 17.5 17.6 17.5 17.5 17.3 17.1 16.8 16.2 16.0 9.2 3.7 -0.2 -1.2 -1.8 -1.1 5.7 8.2 11.4 12.9 15.0 15.6 16.5 16.9 
y= 6 17.2 17.5 17.2 17.5 17.3 17.4 17.3 17.6 17.2 16.8 16.9 17.1 16.7 17.1 16.9 17.2 15.7 14.4 3.4 -1.1 -1.1 -1.1 -2.4 -2.3 -0.8 0.2 5.8 7.4 13.4 13.9 15.5 16.2 
y= 7 17.1 17.0 17.8 17.7 17.4 17.2 17.3 17.1 17.1 16.9 16.7 16.6 16.4 16.8 16.5 16.7 16.4 14.7 3.3 -2.1 -3.1 -1.5 -1.2 -2.2 -1.2 -0.2 2.8 5.5 11.2 13.2 15.0 15.7 
y= 8 17.0 17.5 17.3 17.4 17.0 16.5 16.6 16.8 16.5 16.5 16.5 16.5 16.2 16.0 16.1 15.8 15.8 15.8 6.1 0.3 -3.7 -3.3 -0.7 -0.2 -1.0 -0.8 5.5 8.8 8.0 9.5 14.2 15.2 
y= 9 17.2 17.1 16.9 17.2 17.1 16.5 16.5 16.4 16.2 15.9 16.1 15.9 15.7 15.5 15.6 15.4 15.8 16.1 10.3 3.7 -2.2 -2.8 -1.6 -0.0 3.3 -0.7 1.0 6.4 10.5 9.3 13.3 14.7 
y=10 17.2 16.7 16.7 16.4 16.3 16.4 16.1 16.2 15.9 15.7 14.6 14.6 14.9 14.4 14.6 14.8 15.1 15.7 13.9 11.0 0.5 -1.2 -0.9 -0.7 4.7 8.7 0.2 -0.2 6.5 7.6 10.7 11.9 
y=11 17.2 17.1 16.5 16.0 15.6 15.6 15.7 15.6 14.6 14.6 12.9 13.0 13.0 14.0 14.1 14.4 14.6 15.3 15.0 12.2 4.5 0.3 0.5 0.6 0.4 5.4 7.2 1.1 5.2 7.0 9.9 11.4 
y=12 16.4 16.7 15.8 15.5 14.9 14.1 14.3 14.2 13.0 12.1 11.6 11.9 11.8 12.4 13.8 13.9 14.2 14.5 15.5 13.5 9.0 7.4 1.4 5.7 2.3 0.7 2.0 -0.8 2.6 5.4 9.2 10.4 
y=13 16.4 16.4 15.4 15.0 14.5 13.8 13.8 14.4 12.8 11.6 13.1 13.1 12.7 12.1 12.9 13.5 14.0 14.6 16.0 14.1 10.8 9.4 2.5 3.9 6.3 4.0 2.5 -1.2 2.3 6.1 8.9 10.8 
y=14 16.2 15.5 14.7 14.0 12.6 12.3 13.5 13.4 13.7 14.1 14.1 12.9 11.2 11.0 11.8 12.6 14.2 15.1 16.4 14.5 12.5 11.9 8.8 5.5 2.9 5.2 6.6 7.1 6.6 8.3 11.8 13.3 
y=15 16.3 15.4 14.0 12.9 12.0 11.9 12.0 13.0 14.8 15.1 13.0 11.8 11.0 10.9 12.1 12.4 14.7 15.7 16.0 14.6 12.8 12.2 10.6 9.3 5.0 5.6 8.5 8.9 10.0 10.7 12.9 13.2 
y=16 15.7 15.2 12.2 12.1 12.2 12.0 11.9 12.3 14.9 14.9 12.2 12.1 11.5 12.8 13.6 14.0 16.3 17.4 15.7 15.3 13.7 13.5 12.9 12.3 11.4 11.6 11.1 12.1 12.7 13.6 13.8 14.3 
y=17 15.7 15.1 12.7 12.1 12.2 11.9 12.0 12.5 14.8 14.8 13.6 12.6 12.9 12.9 13.6 14.0 17.4 17.2 15.8 15.4 14.4 14.0 13.4 13.0 12.0 11.9 12.3 13.1 14.1 13.9 14.4 14.7 
y=18 15.5 14.6 13.3 11.8 12.0 11.9 11.8 12.6 14.9 14.8 14.2 14.5 14.6 14.5 15.6 17.0 17.0 16.7 15.8 15.9 14.7 14.7 14.5 14.3 14.5 14.1 14.0 14.5 14.1 14.7 14.8 15.3 
y=19 15.9 15.2 13.2 13.0 11.9 11.8 12.2 13.1 15.1 15.5 15.5 15.2 15.5 15.4 17.1 17.5 17.0 16.3 16.1 16.0 15.4 15.0 14.8 14.8 14.2 14.2 14.7 14.6 15.1 15.2 15.6 15.4 
y=20 16.4 16.7 15.3 14.8 13.3 13.4 14.2 15.0 17.0 17.1 17.5 17.3 17.2 17.5 17.6 17.7 16.1 15.7 15.9 15.7 15.6 15.4 14.9 15.2 15.0 15.2 14.7 15.3 15.6 15.4 15.8 16.0 
y=21 16.6 16.3 16.1 15.8 14.0 13.9 15.2 16.1 17.4 17.1 17.4 17.4 17.7 17.9 17.2 16.8 15.9 15.6 16.2 15.6 15.6 15.3 15.2 15.3 15.0 15.1 15.0 15.0 15.6 16.2 15.9 16.1 
y=22 16.6 16.8 16.8 17.1 16.9 16.9 16.8 17.2 17.3 17.0 17.8 18.1 17.4 16.8 16.2 16.0 15.7 15.9 15.6 16.0 15.9 15.8 15.5 15.8 15.8 15.6 15.4 15.5 15.2 15.9 16.6 16.2 
y=23 17.3 17.2 17.8 17.0 17.1 17.0 17.3 17.4 17.4 17.3 17.2 17.5 16.8 16.8 16.1 15.8 16.1 15.8 16.0 15.7 16.1 15.7 15.7 15.5 15.5 15.7 15.1 15.4 15.3 15.6 16.3 16.4 

Numeric analysis, array size: 768
min: -3.67, max: 18.07, avg: 13.62

ir_cam_v1.0.pyjson file:
{"frame": [
{"x": 0, "y": 0, "t": 28.7}, 
{"x": 1, "y": 0, "t": 28.5}, 
{"x": 2, "y": 0, "t": 28.2},
...
{"x": 30, "y": 23, "t": 28.6}, 
{"x": 31, "y": 23, "t": 28.3}]
, 
"histogram": [
{"t": 26.02, "n": 0}, 
{"t": 33.11, "n": 0}, 
...
{"t": 153.59, "n": 157}, 
{"t": 160.67, "n": 159}]
, 
"min": 26.02, 
"max": 167.76, 
"avg": 84.25}

test browse:
/home/roland/projects/pi_thermal_camera/py_gui/captures/20240206_bakpan/20240206_191906

NB: the histogram part of the JSON is not important, is not used, can be skipped.
'''

import os

class Ansi:
    'Support for the Raspberry Pi IR Camera app ANSI log file with the table of temperatures in txt format'

    msg = 'try it' # values: ok, error X, ansi file not found, json file already exists
    dir_name = ''
    #temp_array = [[]] # 2-dim array, 24 rows, 32 columns
    f_json = None # file handle

    def __init__(self, dir):
        self.dir_name = dir
        self.msg = ''
        filename = f'{self.dir_name}/ansi.txt'
        if self.msg == '' and not os.path.isfile(filename):
            self.msg = f'ansi file not found: {filename}'
        filename = f'{self.dir_name}/log.json'
        if self.msg == '' and os.path.isfile(filename):
            self.msg = f'json file already exists: {filename}'
        else:
            self.msg = 'ok'
        return
    
    def make_json(self):
        'read file dir/ansi.txt and make file log.json'
        if self.msg != 'ok':
            print(f'Ansi.readdir: not OK: {self.msg}. Stop.')
            return
        self.msg = 'making json'
        ansifilename = f'{self.dir_name}/ansi.txt'
        jsonfilename = f'{self.dir_name}/log.json'
        self.f_json = open(jsonfilename, 'w')
        self.to_json('{"frame": [')
        with open(ansifilename, 'r') as file:
            # skip the 8-bit ansi lines
            for _ in range(29):
                file.readline()
            # decode the numeric lines
            comma = ','
            for y in range(24):             
                line = file.readline().rstrip()
                row_hdr = line[0:5]
                row_nrs = line[5:].split()
                #print(f'line: {row_hdr} [0]= {row_nrs[0]}, [31]= {row_nrs[31]}')
                for x in range(32):
                    t = row_nrs[x]
                    # no comma after final array value
                    if x == 31 and y == 23:
                        comma = ''
                    # json line is now complete
                    self.to_json(f'{{"x": {x}, "y": {y}, "t": {t} }} {comma}')
            # final json part
            self.to_json('],')
            file.readline()
            file.readline()
            # min,max,avg
            line = file.readline()
            mma = line.split(',')
            mma_min = mma[0][5:]
            mma_max = mma[1][6:]
            mma_avg = mma[2][6:]
            self.to_json(f'"min": {mma_min},')
            self.to_json(f'"max": {mma_max},')
            self.to_json(f'"avg": {mma_avg} }}')
        # clean up
        self.f_json.close()
        self.msg = 'ok'
        return

    def to_json(self, l):
        'write l to the json output file'
        #print(l) #debug output
        self.f_json.write(f'{l}\n')
        return

if __name__ == "__main__":
    # Demo for using this class
    folder_path = '/home/roland/projects/pi_thermal_camera/py_gui/captures/20240206_bakpan/20240206_191906/'
    ansi = Ansi(folder_path)
    print(f'folder: {ansi.msg}')
    ansi.make_json()
    print(f'done: {ansi.msg}')
    
