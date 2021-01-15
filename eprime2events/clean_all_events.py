#!/usr/bin/env python

import chardet
import csv
import json
import os
import re
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shutil
import time
import zipfile
from chardet import detect
from chardet.universaldetector import UniversalDetector as udet
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from os.path import splitext
from pandas import DataFrame as df
from tqdm import tqdm
from cimaq_utils import flatten
from cimaq_utils import loadimages
from cimaq_utils import get_encoding

from clean_events_lib import loadpaths
from clean_events_lib import getid
from clean_events_lib import makename
from clean_events_lib import get_enc_onsets
from clean_events_lib import get_enc_outputs
from clean_events_lib import get_ret_outputs

def clean_all_events(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
    cimaq_dir = xpu(cimaq_dir)
    frame, prefixes = loadpaths(cimaq_dir)

    enconsets = get_enc_onsets(cimaq_dir)
    encoutputs = get_enc_outputs(cimaq_dir)
    retsheets = get_ret_outputs(cimaq_dir)
    sheetspersub = tuple(zip(frame.index, enconsets, encoutputs, retsheets))

    fullencsheets = [(frame.index[item[0]],
                      pd.concat([item[1][0], item[1][1]], axis=1,
                      sort=False).reset_index(\
                          drop=True).drop("Unnamed: 0", axis=1))
                     for item in enumerate(sheetspersub)]
    
    [item[1].to_csv(join(indir, item[0],
                         item[0]+"_task-Memory_events.tsv"), sep='\t')
     for item in fullencsheets]
    frame['newdirs'] = [xpu(join("~/cimaq_events2021", row[0]))
                                 for row in frame.iterrows()]
    [os.makedirs(ndir, exist_ok=True) for ndir in frame.newdirs]
    oldevnts = flatten([[sheet for sheet in loadimages(join(indir, row[0]))
                         if "task-Memory_events.tsv" in sheet]
                        for row in frame.iterrows()])
    oldrets = flatten([[sheet for sheet in loadimages(join(indir, row[0]))
                         if "_task-retrieval" in sheet]
                        for row in frame.iterrows()])
    newevnts = flatten([[join(row[1]['newdirs'], bname(sheet))
                         for sheet in loadimages(join(indir, row[0]))
                         if "task-Memory_events.tsv" in sheet]
                         for row in frame.iterrows()])
    newrets = flatten([[join(row[1]['newdirs'], bname(sheet))
                         for sheet in loadimages(join(indir, row[0]))
                         if  "_task-retrieval" in sheet]
                         for row in frame.iterrows()])

    evtmvr = tuple(zip(oldevnts, newevnts))
    retmvr = tuple(zip(oldrets, newrets))
    [shutil.move(item[0], item[1]) for item in evtmvr]
    [shutil.move(item[0], item[1]) for item in retmvr]
    savior = tuple(zip(test.sort_index().index,
                       [item[1] for item in fullencsheets]))
    [item[1].to_csv(join(xpu('~/cimaq_events2021'), item[0],
                         item[0]+"_task-Memory_events.tsv"), sep='\t')
     for item in savior]

def main():
    clean_all_events()

if __name__ == '__main__':
    main()
    