#!/usr/bin/env python

# 1) read from a tif movie with multiple frames

import sys
from PIL import Image
import numpy
from ROOT import *

froot = TFile.Open('../results/data.root', 'recreate')

def convert(arr):
    print 'convert'

def process(fname):
    ftree = TTree('tree', 'movie')
    tree.Branch('pixels', )

    im = Image.open(fname)
    nframes = 1
    while im:
        if nframes > 10:
            break
        try:
            print 'processing ... {0}'.format(nframes)
            im.seek(nframes)
            imarray = numpy.array(im)
            convert(imarray)
            # AnalyzeImage(imarray, nframes)
            nframes = nframes + 1
        except EOFError:
            break
    print nframes

def help():
    print './imager file.tif'
    exit(1)


if __name__ == '__main__':
    # verify file
    if len(sys.argv) != 2:
        help()
    fname = sys.argv[1]
    if (len(fname) - fname.find('.tif') != 4 or fname.find('.tif') < 0):
        help()

    process(fname)
    froot.Close()
