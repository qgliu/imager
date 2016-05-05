#!/usr/bin/env python

import sys, math
from PIL import Image
import numpy as np
from ROOT import *
from pymongo import MongoClient

client = MongoClient()
db = client.imager
col_frame = db.frame
froot = TFile.Open('results/im.root', 'recreate')

def ShineOrigin(origin_hit, ring, origin_hit_coord, pixels, pixel_indices, xbin, ybin):
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
            found = np.argwhere(np.array(pixel_indices) == true_coord_1d)
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
        ShineOrigin(origin_hit, ring, origin_hit_coord, pixels, pixel_indices, xbin, ybin)

def FindSingleHit(pixels, pixel_indices, xbin, ybin):
    # print 'FindSingleHit'
    used_index = []
    max_index = np.argmax(pixels)
    used_index.append(max_index)

    # coordinate origin is defined by the max value pixel
    origin_hit_value = pixels[max_index]
    origin_hit_coord = (int(math.fmod(pixel_indices[max_index], xbin)), pixel_indices[max_index]/xbin)

    # origin coordinate
    origin_hit = {}
    origin_hit[(0,0)] = origin_hit_value # append origin

    ShineOrigin(origin_hit, 1, origin_hit_coord, pixels, pixel_indices, xbin, ybin)

    # removed used hits
    for h in origin_hit:
        x,y = h[0], h[1]
        true_coord = (x+origin_hit_coord[0], y+origin_hit_coord[1])
        if (true_coord[0] >= 0 and true_coord[0] <= xbin) and (true_coord[1] >= 0 and true_coord[1] <= ybin):
            true_coord_1d = true_coord[1]*xbin+true_coord[0]
            found = np.argwhere(np.array(pixel_indices) == true_coord_1d)
            if len(found) > 0:
                found = found[0][0]
                pixel_indices.pop(found)
                pixels.pop(found)
        #     else:
        #         print '!found', true_coord
        # else:
        #     print 'out box', true_coord

    values = np.fromiter(iter(origin_hit.values()), dtype='float')
    total = np.sum(values)
    return [origin_hit_coord, total]

def FindHits(pixels, pixel_indices, xbin, ybin, iframe, h3):
    if (iframe%100 == 0):
        print 'FindHits', iframe
    # orignal copy
    org_pixels = pixels
    org_pixel_indices = pixel_indices

    hits = []
    while (len(pixels)>0):
        hit = FindSingleHit(pixels, pixel_indices, xbin, ybin)
        hits.append(hit)

    hits_data  = []
    for hit in hits:
        hits_data.append({
        "x": hit[0][1],
        "y": hit[0][0],
        "size": hit[1]
        })

    result = db.frames.insert_one({
    "iframe": iframe,
    "hits": hits_data
    })
    # for hit in hits:
    #     h3.Fill(hit[0][1],hit[0][0], iframe, hit[1])
    # print len(hits)
    return hits


def FindPixels(arr, mean, std):
    # print 'FindPixels'
    # define significance
    result = np.subtract(arr, mean)
    result = result.clip(min=0)
    result = np.divide(result, std)
    result = np.trunc(result/12.)

    pixel_indices = np.nonzero(result)
    pixels = np.take(arr, pixel_indices)

    # to 1D list
    pixel_indices = pixel_indices[0].tolist()
    pixels = np.ravel(pixels).tolist()
    # print len(pixels)

    return pixels, pixel_indices

def GetSig(fname, mean, std, nframes):
    print 'GetSig'

    shape = np.shape(std)
    h3 = TH3F('h3', '', shape[0], 0, shape[0], shape[1], 0, shape[1], nframes, 0, nframes)

    # 2D to 1D
    std = np.ravel(std)
    mean = np.ravel(mean)

    im = Image.open(fname)
    iframe = 1
    im.seek(iframe)
    try:
        while im:
            im.seek(iframe)
            imarray = np.array(im)
            imarray = np.ravel(imarray)
            pixels, pixel_indices = FindPixels(imarray, mean, std)
            hits = FindHits(pixels, pixel_indices, shape[0], shape[1], iframe-1, h3)
            iframe = iframe+1
    except:
        pass


def GetBkg(fname, nreads=100):
    print 'GetBkg'
    # get total frames ==> nframes
    im = Image.open(fname)
    nframes = 1;
    try:
        while im:
            im.seek(nframes)
            nframes = nframes+1
    except:
        pass
    print nframes, nreads

    # read designated frames
    imStack=[]
    offset = max(0, nframes - nreads - 1)
    im = Image.open(fname)
    iframe = 1
    im.seek(iframe+offset)
    try:
        while im:
            im.seek(iframe+offset)
            imarray = np.array(im)
            imStack.append(imarray)
            iframe = iframe+1
    except:
        pass

    im3D = np.dstack(imStack)
    std = np.std(im3D, axis=(2))
    mean = np.mean(im3D, axis=(2))

    # hmeanLarge: pixels with large standard deviation
    # hmeanZero: pixels with zero standard deviation

    # ROOT output
    shape = np.shape(std)
    stdLarge = 10
    hstd       = TH1F('hstd', '', 100, 0, 10)
    hmean      = TH2F('hmean', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hmeanLarge = TH2F('hmeanLarge', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)
    hmeanZero  = TH2F('hmeanZero', '', shape[0], 0, shape[0]+1, shape[1], 0, shape[1]+1)

    for x in np.nditer(std):
        hstd.Fill(x)
    for index, x in np.ndenumerate(mean):
        hmean.Fill(index[0], index[1], x)
        if std[index[0], index[1]] > stdLarge:
            hmeanLarge.Fill(index[0], index[1], x)
        if std[index[0], index[1]] == 0:
            hmeanZero.Fill(index[0], index[1], x)
    hstd.Write()
    hmean.Write()
    hmeanLarge.Write()
    hmeanZero.Write()

    # restrict std dev to minimum of 1.
    std = np.clip(std, 1, 1000)
    return mean, std, nframes

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print './imager file.tif'
        exit(1)
    fname = sys.argv[1]

    mean, std, nframes = GetBkg(fname, 100)
    GetSig(fname, mean, std, nframes)
    froot.Close()
