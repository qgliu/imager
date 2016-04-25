#!/usr/bin/env python

import sys
from ROOT import *

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print './PrintHist.py RootFile'
        exit(1)
    fin = TFile.Open(sys.argv[1])
    keys = gDirectory.GetListOfKeys()
    print keys
    fin.Close()
