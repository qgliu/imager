from ROOT import TH1F
import numpy as np

class Pixel:
    data = 0
    mean = 0
    std = 0
    xbin_min = 50;
    def __init__(self, data):
        self.data = data

    def Print(self):
        print self.data

    def Analyze(self, x, y, h3):
        mean = np.std(self.data[-100:])
        std = np.std(self.data[-100:])
        threshold = mean+10*std

        for ibin in range(len(self.data)):
            if self.data[ibin]> threshold:
                h3.SetBinContent(x,y,ibin, self.data[ibin])
        return threshold

    def GetH1(self, hname='h1'):
        m = max(self.data)
        h = TH1F(hname,'', max(m, self.xbin_min), 0, max(m, self.xbin_min))
        for value in self.data:
            h.Fill(value)
        return h
