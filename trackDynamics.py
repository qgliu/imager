#!/usr/bin/env python

import sys
from ROOT import *
from array import array
import numpy as np
from pymongo import MongoClient
import csv

client = MongoClient()
db = client.imager

pixel_size = 0.25 # mm
frame_gap = 300 # ps
factor = pixel_size*0.001/(0.3*0.000000001)

def Slope(inputs):
    # inputs are a array of [[x, y, iframe], ...]
    # outputs will be in the same form
    inputs = sorted(inputs, key=lambda x: x[2])
    # for values in inputs:
        # print values
    outputs = []
    for index, values in enumerate(inputs):
        if (index == 0):
            outputs.append([0, 0, values[2]])
        elif (index<100):
            sx = (values[0]-inputs[0][0])/float(index)*factor
            sy = (values[1]-inputs[0][1])/float(index)*factor
            outputs.append([sx, sy, values[2]])
        else:
            sx = (values[0]-inputs[index-100][0])/float(index)*factor
            sy = (values[1]-inputs[index-100][1])/float(index)*factor
            outputs.append([sx, sy, values[2]])
            # print values[0], inputs[index-50][0], index, [sx, sy, values[2]]
    return outputs

def GetGraphics(inputs):
    arr = np.array(inputs)
    arr = arr.T
    # print np.asfarray(arr[0], dtype='float')
    print len(arr[0]), np.asfarray(arr[2], dtype='float'), np.asfarray(arr[0], dtype='float')
    gr_x = TGraph(len(arr[0]), array('f', arr[2]), array('f', arr[0]))
    gr_y = TGraph(len(arr[0]), array('f', arr[2]), array('f', arr[1]))
    gr_x.SetTitle('x-axis')
    gr_y.SetTitle('y-axis')
    gr_x.GetXaxis().SetTitle('frame index')
    gr_y.GetXaxis().SetTitle('frame index')
    return gr_x, gr_y

def TrackDynamics(cursor):
    for index, track in enumerate(cursor):
        if len(track['hits'])<2000:
            continue
        positions = []
        for hit in track['hits']:
            positions.append([hit['x'], hit['y'], hit['iframe']])
        # print positions
        velocities = Slope(positions)
        accelerations = Slope(velocities)

        pos_x, pos_y = GetGraphics(positions)
        vel_x, vel_y = GetGraphics(velocities)
        acc_x, acc_y = GetGraphics(accelerations)
        pos_x.GetYaxis().SetTitle('Position')
        pos_y.GetYaxis().SetTitle('Position')
        vel_x.GetYaxis().SetTitle('Velocity (m/s)')
        vel_y.GetYaxis().SetTitle('Velocity (m/s)')
        acc_x.GetYaxis().SetTitle('Acceleration (m/s^2)')
        acc_y.GetYaxis().SetTitle('Acceleration (m/s^2)')

        canvas = TCanvas('canvas', '', 800, 1200)
        canvas.Divide(2,3)
        canvas.cd(1)
        pos_x.Draw()
        canvas.cd(2)
        pos_y.Draw()
        canvas.cd(3)
        vel_x.Draw()
        canvas.cd(4)
        vel_y.Draw()
        canvas.cd(5)
        acc_x.Draw()
        acc_x.SetMaximum(500000000)
        acc_x.SetMinimum(-500000000)
        canvas.cd(6)
        acc_y.Draw()
        acc_y.SetMaximum(500000000)
        acc_y.SetMinimum(-500000000)
        canvas.Print('tmp.pdf')
        # # print velocities
        # hvel_x = TH1F('hvel_x_{0}'.format(index), '', 4500,0,4500)
        # hvel_y = TH1F('hvel_y_{0}'.format(index), '', 4500,0,4500)
        # for values in velocities:
        #     hvel_x.SetBinContent(values[2], values[0])
        #     hvel_y.SetBinContent(values[2], values[1])
        # canvas = TCanvas('canvas', '', 800, 400)
        # canvas.Divide(2,1)
        # canvas.cd(1)
        # hvel_x.Draw()
        # canvas.cd(2)
        # hvel_y.Draw()
        # canvas.Print('tmp_vel.pdf')
        # accelerations = Slope(velocities)
        # hacc_x = TH1F('hacc_x_{0}'.format(index), '', 4500,0,4500)
        # hacc_y = TH1F('hacc_y_{0}'.format(index), '', 4500,0,4500)
        # for values in accelerations:
        #     print values
        #     hacc_x.SetBinContent(values[2], values[0])
        #     hacc_y.SetBinContent(values[2], values[1])
        # canvas = TCanvas('canvas', '', 800, 400)
        # canvas.Divide(2,1)
        # canvas.cd(1)
        # hacc_x.Draw()
        # canvas.cd(2)
        # hacc_y.Draw()
        # canvas.Print('tmp_acc.pdf')

        break




if __name__=='__main__':
    cursor = db.track18158.find()
    TrackDynamics(cursor)
