#!/usr/bin/env python

import sys
from ROOT import *
from array import array
from pymongo import MongoClient
import csv

client = MongoClient()
db = client.imager


def FindMatchedTrack(cursor_c2, max_time_c1):
    matched_index  = -1
    time_diff = 9999
    time_diff_prev = time_diff
    cursor_c2.rewind()
    for index, track in enumerate(cursor_c2):
        if len(track['hits'])<2000:
            continue
        max_time  = 0;
        max_size = 0;
        for hit in track['hits']:
            if hit['size']>max_size:
                max_size = hit['size']
                max_time = hit['iframe']
        if time_diff > abs(max_time-max_time_c1):
            time_diff_prev = time_diff
            time_diff = abs(max_time-max_time_c1)
            matched_index = index
    print matched_index, time_diff
    if time_diff > 50:
        return None, None, None, None
    else:
        hist_c2 = TH2F('hist_c2_{0}'.format(matched_index), '', 386, 0, 386, 386, 0, 386)
        cursor_c2.rewind()
        track = cursor_c2[matched_index]
        for hit in track['hits']:
            hist_c2.Fill(hit['x'], hit['y'], hit['size'])
        hist_c2.GetXaxis().SetTitle('Start: {0}, end: {1}'.format(track['hits'][-1]['iframe'], track['hits'][0]['iframe']))
        return hist_c2, matched_index, time_diff, time_diff_prev


def MatchTracks(cursor_c1, cursor_c2):
    cursor_c1.rewind()
    for index, track in enumerate(cursor_c1):
        if len(track['hits'])<2000:
            continue
        max_time  = 0
        max_size  = 0
        hist_c1 = TH2F('hist_c1_{0}'.format(index), '', 386, 0, 386, 386, 0, 386)
        for hit in track['hits']:
            hist_c1.Fill(hit['x'], hit['y'], hit['size'])
            if hit['size']>max_size:
                max_size = hit['size']
                max_time = hit['iframe']
        hist_c1.GetXaxis().SetTitle('Start: {0}, end: {1}'.format(track['hits'][-1]['iframe'], track['hits'][0]['iframe']))
        print index, max_time
        hist_c2, matched_index, time_diff, time_diff_prev = FindMatchedTrack(cursor_c2, max_time)

        canvas = TCanvas('canvas', '', 800,400)
        canvas.Divide(2,1)
        canvas.cd(1)
        hist_c1.Draw('COLZ')
        canvas.cd(2)
        if hist_c2:
            hist_c1.SetTitle('Time diff: {0}, next: {1}'.format(time_diff, time_diff_prev))
            hist_c2.Draw('COLZ')
        else:
            print 'no match'

        canvas.Print('matchedTrack_{0}.pdf'.format(index))


if __name__=='__main__':
    cursor_c1 = db.track18158.find()
    cursor_c2 = db.tracks.find()
    MatchTracks(cursor_c1, cursor_c2)
