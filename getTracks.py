#!/usr/bin/env python

import sys, math
import numpy as np
from pymongo import MongoClient

sys.setrecursionlimit(5000)
client = MongoClient()
db = client.imager

tracks = []

def FindNextHit(track, frames):
    lasthit = track[-1]
    # print lasthit
    nextiframe = lasthit['iframe']-1
    neighborhits = []
    for i, hit in enumerate(frames[nextiframe]):
        if abs(hit['x']-lasthit['x'])<=2 and abs(hit['y']-lasthit['y'])<=2:
            hit['index'] = i
            neighborhits.append(hit)

    if len(neighborhits) == 0:
        return
    diff = 9999
    closest_index = 0
    for i, hit in enumerate(neighborhits):
        if abs(hit['size']-lasthit['size']) < diff:
            diff = abs(hit['size']-lasthit['size'])
            closest_index = i
    neighborhits[closest_index]['iframe']=nextiframe
    track.append(neighborhits[closest_index])
    del frames[lasthit['iframe']-1][neighborhits[closest_index]['index']]
    FindNextHit(track, frames)

def FindTrack(i, frames):
    hit = frames[i][0]
    hit['iframe'] = i
    track = []
    track.append(hit)
    del frames[i][0]

    FindNextHit(track, frames)

    result = db.tracks.insert_one({
    "hits": track
    })

    tracks.append(track)

if __name__ == '__main__':
    cursor = db.frames.find()
    frames = []
    for doc in cursor:
        frames.append(doc['hits'])
    # start from the last frame
    framesClone = frames
    print len(frames[0])
    print frames[0]
    for i in reversed(range(1,len(frames))):
        while(len(frames[i])>0):
            FindTrack(i, frames)
    print 'total tracks', len(tracks)
