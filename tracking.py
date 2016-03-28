# analyze signal
# findPixels: find significant pixels
# findHits: clustering pixels
# findSingleHit: based on the max value point to find the hit

import numpy, math
from ROOT import *

def shineOrigin(origin_hit, ring, origin_hit_coord, pixels, pixel_indices, xbin, ybin):
    square_coord = []
    # horizontal side
    for i in range(-ring, ring+1):
        square_coord.append([i, ring])
        square_coord.append([i, -ring])
    # vertical side, skip duplicates
    for i in range(-ring+1, ring):
        square_coord.append([ring, i])
        square_coord.append([-ring, i])

    square_found = 0
    for coord in square_coord:
        x, y = coord[0], coord[1]
        inners = []
        # if abs(x)-1>0:
        #     inners.append((x/abs(x)*(abs(x)-1), y))
        # if abs(y)-1>0:
        #     inners.append((x, y/abs(y)*(abs(y)-1)))
        if abs(x)-1>0 and abs(y)-1>0:
            inners.append((x/abs(x)*(abs(x)-1),y/abs(y)*(abs(y)-1)))
        if len(inners)==0:
            inners.append((0, 0))
        min_value = 9999999;
        for inner in inners:
            min_value = min(min_value, origin_hit[inner])
        true_coord = (x+origin_hit_coord[0], y+origin_hit_coord[1])
        if (true_coord[0] > 0 and true_coord[0] <= xbin) and (true_coord[1] > 0 and true_coord[1] <= ybin):
            true_coord_1d = true_coord[1]*xbin+true_coord[0]
            found = numpy.argwhere(numpy.array(pixel_indices) == true_coord_1d)
            if len(found) > 0:
                found = found[0][0]
                if pixels[found] <= min_value:
                    origin_hit[(x, y)] = pixels[found]
                    square_found = square_found+1
                else:
                    origin_hit[(x, y)] = 0
            else:
                origin_hit[(x, y)] = 0
        else:
            origin_hit[(x, y)] = 0
    if (square_found>0):
        ring = ring+1
        shineOrigin(origin_hit, ring, origin_hit_coord, pixels, pixel_indices, xbin, ybin)


def findSingleHit(pixels, pixel_indices, xbin, ybin):
    used_index = []
    max_index = numpy.argmax(pixels)
    used_index.append(max_index)

    # coordinate origin is defined by the max value pixel
    origin_hit_value = pixels[max_index]
    origin_hit_coord = (int(math.fmod(pixel_indices[max_index], xbin)), pixel_indices[max_index]/xbin)

    # origin coordinate
    origin_hit = {}
    origin_hit[(0,0)] = origin_hit_value # append origin

    shineOrigin(origin_hit, 1, origin_hit_coord, pixels, pixel_indices, xbin, ybin)

    # removed used hits
    for h in origin_hit:
        x,y = h[0], h[1]
        true_coord = (x+origin_hit_coord[0], y+origin_hit_coord[1])
        if (true_coord[0] > 0 and true_coord[0] <= xbin) and (true_coord[1] > 0 and true_coord[1] <= ybin):
            true_coord_1d = true_coord[1]*xbin+true_coord[0]
            found = numpy.argwhere(numpy.array(pixel_indices) == true_coord_1d)
            if len(found) > 0:
                found = found[0][0]
                pixel_indices.pop(found)
                pixels.pop(found)

    values = numpy.fromiter(iter(origin_hit.values()), dtype='float')
    average = numpy.sum(values)/numpy.count_nonzero(values)
    return [origin_hit_coord, average]

def findHits(pixels, pixel_indices, xbin, ybin, iframe):
    # orignal copy
    org_pixels = pixels
    org_pixel_indices = pixel_indices

    hits = []
    while (len(pixels)>0):
        hit = findSingleHit(pixels, pixel_indices, xbin, ybin)
        hits.append(hit)
    #     print len(pixels)
    # print hits

    hhits  = TH2F('hhits_{0:04d}'.format(iframe), '', xbin, 0, xbin+1, ybin, 0, ybin+1)
    for hit in hits:
        hhits.Fill(hit[0][0],hit[0][0],hit[1])
    hhits.Write()
    return hits

def findPixels(arr, mean, std, iframe):
    # define significance
    result = numpy.absolute(numpy.subtract(arr, mean))
    result = numpy.divide(result, std)
    result = numpy.trunc(result/12.)

    pixel_indices = numpy.nonzero(result)
    pixels = numpy.take(arr, pixel_indices)

    # to 1D list
    pixel_indices = pixel_indices[0].tolist()
    pixels = numpy.ravel(pixels).tolist()

    return pixels, pixel_indices

def analyze(arrStack, mean, std):
    print 'tracking.analyze ...'
    shape = numpy.shape(std)
    hsig  = TH2F('hsig', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hsigw = TH1F('hsigw', '', 100, 0, 50)

    # 2D to 1D
    std = numpy.ravel(std)
    mean = numpy.ravel(mean)

    for i, arr in enumerate(arrStack):
        hsig_tmp  = TH2F('hsig_{0:04d}'.format(i), '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
        # print 'hsig_{0:04d}'.format(i)

        arr = numpy.ravel(arr)
        pixels, pixel_indices = findPixels(arr, mean, std, i)
        hits = findHits(pixels, pixel_indices, shape[0], shape[1], i)

        for index, x in numpy.ndenumerate(pixels):
            hsig.Fill(math.floor(pixel_indices[index[0]]/shape[0]), math.fmod(pixel_indices[index[0]], shape[0]), x)
            hsig_tmp.Fill(math.floor(pixel_indices[index[0]]/shape[0]), math.fmod(pixel_indices[index[0]], shape[0]), x)
        hsig_tmp.Write()

    hsig.Write()
    # hsigw.Write()
