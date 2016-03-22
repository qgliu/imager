# analyze signal

import numpy
from ROOT import *

def analyze(arrStack, mean, std):
    shape = numpy.shape(std)
    hsig  = TH2F('hsig', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hsigw = TH1F('hsigw', '', 100, 0, 50)

    for arr in arrStack:
        result = numpy.absolute(numpy.subtract(arr, mean))
        result = numpy.divide(result, std)
        for index, x in numpy.ndenumerate(arr):
            if result[index[0], index[1]] > 7:
                hsig.Fill(index[0], index[1], x)
                hsigw.Fill(result[index[0], index[1]])

    hsig.Write()
    hsigw.Write()
