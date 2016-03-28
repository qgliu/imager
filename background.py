# analyze background
# 1) use the set of (ideally) signal-free images to estimate background distributions, pixel by pixel
# 2) take a list of 2D images/array
# 3) write to ROOT and json files

import numpy, json
from ROOT import *

def analyze(list2Dimage):
    print 'background.analyze ...'
    # get std, mean of each pixel
    std  = numpy.std(list2Dimage, axis  =(2))
    mean = numpy.mean(list2Dimage, axis =(2))

    # hmeanLarge: pixels with large standard deviation
    # hmeanZero: pixels with zero standard deviation

    # ROOT output
    shape = numpy.shape(std)
    stdLarge = 10
    hstd       = TH1F('hstd', '', 100, 0, 10)
    hmean      = TH2F('hmean', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hmeanLarge = TH2F('hmeanLarge', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hmeanZero  = TH2F('hmeanZero', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)

    for x in numpy.nditer(std):
        hstd.Fill(x)
    for index, x in numpy.ndenumerate(mean):
        hmean.Fill(index[0], index[1], x)
        if std[index[0], index[1]] > stdLarge:
            hmeanLarge.Fill(index[0], index[1], x)
        if std[index[0], index[1]] == 0:
            hmeanZero.Fill(index[0], index[1], x)
    hstd.Write()
    hmean.Write()
    hmeanLarge.Write()
    hmeanZero.Write()

    # json output
    std_data = [];
    mean_data = [];
    for index, value in numpy.ndenumerate(std):
        std_data.append({'x': index[0], 'y': index[1], 'value': value})
    for index, value in numpy.ndenumerate(mean):
        mean_data.append({'x': index[0], 'y': index[1], 'value': value})
    with open('results/im.json', 'w+') as outfile:
        json.dump({"background": {"std": std_data}}, outfile)
        json.dump({"background": {"mean": mean_data}}, outfile)

    # restrict std dev to minimum of 1.
    std = numpy.clip(std, 1, 1000)
    return mean, std
