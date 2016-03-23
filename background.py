# analyze background

import numpy
from ROOT import *

def analyze(arr3D):
    print 'background.analyze ...'
    std  = numpy.std(arr3D, axis  =(2))
    mean = numpy.mean(arr3D, axis =(2))

    shape = numpy.shape(std)
    hstd       = TH1F('hstd', '', 100, 0, 10)
    hmean      = TH2F('hmean', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hmeanLarge = TH2F('hmeanLarge', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hmeanZero  = TH2F('hmeanZero', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)

    for x in numpy.nditer(std):
        hstd.Fill(x)
    for index, x in numpy.ndenumerate(mean):
        hmean.Fill(index[0], index[1], x)
        if std[index[0], index[1]]>10:
            hmeanLarge.Fill(index[0], index[1], x)
        if std[index[0], index[1]]==0:
            hmeanZero.Fill(index[0], index[1], x)
    hstd.Write()
    hmean.Write()
    hmeanLarge.Write()
    hmeanZero.Write()

    # restrict std dev to minimum of 1.
    std = numpy.clip(std, 1, 1000)
    return mean, std
