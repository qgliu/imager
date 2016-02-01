#!/usr/bin/env python

import sys
from PIL import Image
import numpy
from ROOT import *

def Array2dto1d(arr):
    print arr.size


def ReadImage(fname):
    im = Image.open(fname)
    imarray = numpy.array(im)
    Array2dto1d(imarray)

if __name__ == '__main__':
    # verify file
    if len(sys.argv) != 2:
        print './imager file.tif'
        exit(1)
    fname = sys.argv[1]
    if (len(fname) - fname.find('.tif') != 4 or fname.find('.tif') < 0):
        print './imager file.tif (need a tif file)'
        exit(1)

    ReadImage(fname)
