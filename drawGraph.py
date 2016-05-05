#!/usr/bin/env python

import sys
from ROOT import *
from array import array

if __name__=='__main__':
    if len(sys.argv) != 2:
        print './drawGraph log'
        exit(1)
    fname = sys.argv[1]

    hits = []
    for line in open(fname):
        hits.append(int(line))
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
    canvas.Print('hits_stat.png')
    canvas.Print('hits_stat.pdf')
