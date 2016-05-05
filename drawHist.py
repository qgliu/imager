#!/usr/bin/env python

import sys
from ROOT import *
from array import array
from pymongo import MongoClient

client = MongoClient()
db = client.imager

def DrawHitSize(cursor):
    max_size = 0;
    min_size = 10000;
    h = TH2F('h','',cursor.count(), 0, cursor.count(), 10000, 0, 10000)
    for doc in cursor:
        hits = doc['hits']
        for hit in hits:
            if hit['size']>max_size:
                max_size = hit['size']
            if hit['size']<min_size:
                min_size = hit['size']
            h.Fill(doc['iframe'], hit['size'])

    canvas = TCanvas()
    h.Draw()
    h.GetXaxis().SetTitle('Frame index')
    h.GetYaxis().SetTitle('Hit size')
    h.SetTitle('Max: {0} Min: {1}'.format(max_size, min_size))
    canvas.Print('hitsize.pdf')

    hprofile = h.ProfileX()
    hprofile.Draw()
    canvas.Print('hitsize_profile.pdf')

def DrawNumberofHits(cursor):
    hits = []
    for doc in cursor:
        hits.append(len(doc['hits']))

    index = range(1, len(hits)+1)
    hits = array('f', hits)
    index = array('f', index)
    gr = TGraph(len(hits), index, hits)

    canvas = TCanvas()
    gr.SetLineColor(kBlue)
    gr.SetLineWidth(2)
    gr.Draw('AC')
    gr.SetTitle('Found hits in each frame')
    gr.GetXaxis().SetTitle('Frame index')
    gr.GetYaxis().SetTitle('Number of hits')
    canvas.Print('hits_stat.pdf')


if __name__=='__main__':
    cursor = db.frames.find()
    # DrawNumberofHits(cursor)
    DrawHitSize(cursor)
