#!/usr/bin/env python

import sys
from ROOT import *
from array import array
from pymongo import MongoClient
import csv

client = MongoClient()
db = client.imager

def DrawTrackIntensity(cursor):
    hist = []
    count = 0
    for doc in cursor:
        if len(doc['hits'])<2000:
            continue
        count=count+1
        h = TH1F('h{0}'.format(count), '', 4500,0,4500)
        # h = TH2F('h{0}'.format(count),'',500,0,500,500,0,500)
        for hit in doc['hits']:
            # h.Fill(hit['x'],hit['y'],hit['size'])
            h.SetBinContent(hit['iframe'], hit['size'])
        h.SetLineColor(kBlue)
        h.SetLineWidth(2)
        hist.append(h)
    print len(hist)

    canvas= TCanvas()
    hist[0].Draw('L')
    canvas.Print('trackIntensity.pdf(', 'pdf')
    for h in hist[1:-1]:
        h.Draw('L')
        canvas.Print('trackIntensity.pdf', 'pdf')
    hist[-1].Draw('L')
    canvas.Print('trackIntensity.pdf)', 'pdf')


def DrawTrack(cursor):
    hist = []
    count = 0
    for doc in cursor:
        if len(doc['hits'])<2000:
            continue
        count=count+1
        h = TH2F('h{0}'.format(count),'',500,0,500,500,0,500)
        for hit in doc['hits']:
            h.Fill(hit['x'],hit['y'],hit['size'])
        h.SetMarkerColor(count%10+1)
        hist.append(h)
    print len(hist)

    canvas= TCanvas()
    hist[0].Draw()
    for h in hist[1:]:
        h.Draw('same')
    hist[0].SetTitle('{0} selected tracks'.format(len(hist)))
    canvas.Print('track2D.pdf')
    canvas.Print('track2D.png')

def ExportToExcel(cursor):
    count = 1
    for doc in cursor:
        if len(doc['hits'])<2000:
            continue
        with open('track_{0}.csv'.format(count), 'wb') as csvfile:
            fout = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for hit in doc['hits']:
                row = [hit['iframe'], hit['x'], hit['y'], hit['size']]
                # print row
                fout.writerow(row)

        count = count+1

def DrawNumberofTrack(cursor):
    h = TH1F('h','',5000,0,5000)
    max_size = 0
    min_size = 5000
    for doc in cursor:
        if len(doc['hits'])>20:
            h.Fill(len(doc['hits']))
        if max_size < len(doc['hits']):
            max_size = len(doc['hits'])
        if min_size > len(doc['hits']):
            min_size = len(doc['hits'])

    canvas = TCanvas()
    h.SetLineColor(kBlue)
    h.SetLineWidth(2)
    h.Draw()
    h.SetTitle('Max: {0}, Min: {1}'.format(max_size, min_size))
    h.GetXaxis().SetTitle('Number of hits in a track')
    canvas.Print('tracks_stat.pdf')
    canvas.Print('tracks_stat.png')


if __name__=='__main__':
    cursor = db.tracks.find()
    # DrawNumberofTrack(cursor)
    # DrawTrack(cursor)
    # ExportToExcel(cursor)
    DrawTrackIntensity(cursor)
