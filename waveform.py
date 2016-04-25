#!/usr/bin/env python

# 1) read from a tif movie with multiple frames
# 2) save background histograms
# 3) draw

import sys
from PIL import Image
import numpy
from ROOT import *

import background as bkg
import tracking

from classes.pixel import Pixel

# froot = TFile.Open('results/im.root', 'recreate')

def writeRoot(data):
    fout = TFile.Open('results/waveform.root', 'recreate')
    # print data
    data = numpy.dstack(data)
    print data.shape
    print data[2,0]
    vec_list = []
    h3 = TH3F('h3', '', data.shape[0], 0, data.shape[0], data.shape[1], 0, data.shape[1], data.shape[2], 0, data.shape[2])
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            tmp = Pixel(data[x,y])
            threshold = tmp.Analyze(x, y, h3)
    h3.Write()
    fout.Close()
    # vec = vector('double')()
    # for value in data:
    #     print value.shape


def AnalyzeImage(arr, index):
    xmin = numpy.amin(arr)
    xmax = numpy.amax(arr)
    shape = numpy.shape(arr)
    inclusive = TH1F('inclusive_{0:d}'.format(index), '', 10,0,10)
    signal_1d = TH1F('signal1D_{0:d}'.format(index), '', xmax-xmin+1, xmin, xmax)
    signal_2d = TH2F('signal2D_{0:d}'.format(index), '', shape[0], 0, shape[0], shape[1], 0, shape[1])
    for index, x in numpy.ndenumerate(arr):
        inclusive.Fill(x)
        if x>40:
            signal_1d.Fill(x)
            signal_2d.Fill(index[0], index[1], x)
    inclusive.Write()
    signal_1d.Write()
    signal_2d.Write()

def RetrieveImage(fname):
    arrStack = [];
    im = Image.open(fname)
    nframes = 1
    while im:
        # if nframes>10:
        #     break
        try:
            if nframes%100==0:
                print 'processing ... {0}'.format(nframes)
            im.seek(nframes)
            imarray = numpy.array(im)
            arrStack.append(imarray)
            # if nframes==1:
            #     AnalyzeImage(imarray, nframes)
            nframes = nframes + 1
        except:
            break
    writeRoot(arrStack)
    # arr3D = numpy.dstack(arrStack[max(0,len(arrStack)-100):])
    # print arr3D.shape
    # mean, std = bkg.analyze(arr3D)
    # tracking.analyze(arrStack, mean, std)
    # print nframes

if __name__ == '__main__':
    # verify file
    if len(sys.argv) != 2:
        print './imager file.tif'
        exit(1)
    fname = sys.argv[1]
    if (len(fname) - fname.find('.tif') != 4 or fname.find('.tif') < 0):
        print './imager file.tif (need a tif file)'
        exit(1)

    RetrieveImage(fname)
    # froot.Close()
