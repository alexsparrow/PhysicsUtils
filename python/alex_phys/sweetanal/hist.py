#!/usr/bin/env python
import sys

class Hist:
    def __init__(self, low, high, bins):
        self._bins = [0]*bins
        self._bin_width = (high - low)/bins
        self._bin_lows = [low + i*self._bin_width for i in range(bins)]
        self._low = low
        self._high = high
        self._underflow = 0
        self._overflow = 0

    def fill(self, val, weight=1):
        ibin = int(len(self._bins)/2)
        binlow = 0
        binhigh = len(self._bins) -1
        it = 0
        if val >= self._high:
            self._overflow += weight
            return
        if val <= self._low:
            self._underflow += weight
            return
        while True:
            if val >= self._bin_width*ibin:
                binlow = ibin
                ibin = ibin + int((binhigh - ibin)/2)
            else:
                binhigh = ibin
                ibin = binlow + int((ibin-binlow)/2)
            if (binhigh - binlow) <= 2:
                if val >= binhigh*self._bin_width:
                    ibin = binhigh
                    break
                elif val >= ibin*self._bin_width:
                    break
                else:
                    ibin = binlow
                    break
        self._bins[ibin] += weight

    def bins(self):
        return self._bin_lows

    def values(self):
        return self._bins


if __name__ == "__main__":
    h = Hist(0, 100, 10)
    h.fill(100)
    print h._bins

