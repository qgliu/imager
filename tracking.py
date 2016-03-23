# analyze signal

import numpy, math
from ROOT import *

def analyze(arrStack, mean, std):
    print 'tracking.analyze ...'
    shape = numpy.shape(std)
    hsig  = TH2F('hsig', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hsigw = TH1F('hsigw', '', 100, 0, 50)

    # 2D to 1D
    std = numpy.ravel(std)
    mean = numpy.ravel(mean)

    for arr in arrStack:
        arr = numpy.ravel(arr)

        result = numpy.absolute(numpy.subtract(arr, mean))
        result = numpy.divide(result, std)
        result = numpy.trunc(result/12.)

        signal_indices = numpy.nonzero(result)
        signals = numpy.take(arr, signal_indices)

        # to 1D list
        signal_indices = signal_indices[0].tolist()
        signals = numpy.ravel(signals)

        for index, x in numpy.ndenumerate(signals):
            # print math.floor(signal_indices[index[0]]/shape[0]), math.fmod(signal_indices[index[0]], shape[0]), x
            hsig.Fill(math.floor(signal_indices[index[0]]/shape[0]), math.fmod(signal_indices[index[0]], shape[0]), x)

    hsig.Write()
    # hsigw.Write()
