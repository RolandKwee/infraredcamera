'''
Hist.py
Purpose: create a histogram from the JSON Ir-Cam file
'''

import os.path
import json

class Hist:
    'histogram support, read json file and produce a number of bins'

    min = 0
    avg = 0
    max = 0
    frame = []
    log = None

    bin_t = []
    bin_n = []

    def __init__(self, jsonfile, log):
        'automatic initializer'
        self.log = log
        self.log(f'creating histogram from {jsonfile}')
        if os.path.isfile(jsonfile):
            f = open(jsonfile, 'r')
            j = json.load(f)
            f.close()
            self.min = j['min']
            self.max = j['max']
            self.avg = j['avg']
            self.frame = j['frame']
            self.log(f'min={self.min}, avg={self.avg}, max={self.max}, n={len(self.frame)}')
            #self.bins(10)
            #self.counts([17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 40, 50, 60, 70, 80, 90, 100])
            n = 10
            k = 0.01
            log(f'computing {n} bins with k = {k}, formula: n^2 + k*n')
            self.bin_t = self.compute_bins(self.min, self.max, n, k)
            log(f't: {self.format_list(self.bin_t)}')
            self.bin_n = self.counts(self.bin_t)
            log(f'n: {self.format_list(self.bin_n)}')
        else:
            log(f'Hist error: json file not found: {jsonfile}')
        return

    def format_list(self, l):
        'return string with members of list l taking all the same space'
        s = ''
        for v in l:
            s = f'{s} {v:>3}'
        return s

    def round(self, value, margin):
        'return value rounded to margin (only to whole number is supported)'
        value = int(value + 0.5)
        return value

    def compute_bins(self, tmin, tmax, n, k):
        'use 2nd order polynomial to compute a list of bin limit values'
        # old formula: t = A * i**k + tmin where 0 <= i < n
        # new formula, real 2nd order polynomial: t = A(i^2 + k*i) + tmin
        # round min/max to meaningful values
        tmin = int(tmin + 1) # round down, no up
        tmax = int(tmax + 1) # round up
        # find factor A
        A = (tmax - tmin) / ((n-1)*(n-1) + k*(n-1))
        # fill array
        bin_t = []
        for i in range(n):
            t = self.round(A * (i*i + k*i) + tmin, 0.5)
            bin_t.append(t)
        #print(f'k: {k}, bins:{bin_t}')
        return bin_t

    def counts(self, bins):
        'given a bin array of temperatures, count number for each bin up to that temp'
        # prepare output array
        bin_n = []
        for b in bins:
            bin_n.append(0) # create output array
        # count
        ibin = 0
        for i, f in enumerate(sorted(self.frame, key=lambda x: x['t'])):
            while bins[ibin] < f['t']:
                ibin = ibin + 1
            bin_n[ibin] = bin_n[ibin] + 1
        #endfor
        # output
        #print(f'counts:      {bin_n}')
        #for i, b in enumerate(bin_n):
        #    print(f't up to {bins[i]}: {b}')
        return bin_n

    def get_bin(self, t):
        'return the bin nr for temperature t'
        b = 0
        for i in range(10):
            if t < self.bin_t[i]:
                b = i
                break
        return b

    def bins_obsolete(self, nrbins):
        'create a nr of bins, linear'
        step = (self.max - self.min) / nrbins
        if step < 0.1:
            step = 0.1
        elif step < 1:
            step = 1
        elif step < 10:
            step = 10
        else:
            step = 50
        #endif
        min = step * int(self.min / step)
        max = step * int((self.max + 0.5 * step) / step)
        nrbins = int((max - min) / step)
        self.log(f'bins: step={step}, min={min}, max={max}, n={nrbins}')
        bin_t = []
        bin_n = []
        t = min
        for i in range(0, nrbins):
            t = t + step
            bin_t.append(t)
            bin_n.append(0)
        print(f'bin_t: {bin_t}')
        ibin = 0
        # linear scan of temperature array
        for i, f in enumerate(sorted(self.frame, key=lambda x: x['t'])):
            while bin_t[ibin] < f['t']:
                ibin = ibin + 1
            bin_n[ibin] = bin_n[ibin] + 1
        #endfor
        print(f'bin_n: {bin_n}')
        return
            
            
        
        
