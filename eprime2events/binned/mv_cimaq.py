#!/usr/bin/env python

import csv
import ctypes
import json
import os
import re
import sys
import numpy as np
import pandas as pd
import shutil
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df
from cimaq_utils import flatten
from cimaq_utils import loadimages

def mv_cimaq(outdir="~/extracted_eprime0"):
    outdir = xpu(outdir)
    participants = pd.read_csv(join(outdir, "participants.tsv"), sep='\t').set_index("sub-ID")
    participants['nitems'] = [len(ls(join(outdir, row[0]))) for row in participants.iterrows()]
    
    # Move good files to new BIDS folder
    [[shutil.move(join(row[1]["extdirpaths"], bname(item)), join(xpu("../item")))
      for item in ls(row[1]["extdirpaths"]) if item.endswith(".txt")
     and bool(".edat2" or "PRATIQUE" not in item) == True]
     for row in participants.iterrows()]
    
    participants.to_csv(join(outdir, "participants.tsv"), sep='\t')

def main():
    mv_cimaq()

if __name__ == '__main__':
    main()
    
