#!/usr/bin/env python

import numpy

indices = [1, 2, 11, 23, 243]
# indices = numpy.array(indices)
print numpy.argwhere(numpy.array(indices)==23)
