#!/usr/bin/env python
# encoding: utf-8

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
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from os.path import splitext
from pandas import DataFrame as df
from cimaq_utils import flatten
from cimaq_utils import loadimages
from NEW_extract_events2 import NEW_extract_events2
from chardet.universaldetector import UniversalDetector
# p1 = pd.read_csv("~/extracted_eprime_AS_FWF/participants.tsv", sep='\t')

def NEW_get_allsheetsdf(participants_sheet_path="~/extracted_eprime_AS_FWF/participants.tsv"):
    
    '''Generate DataFrame indexing participants and their respective files'''
    maindir = xpu(dname(participants_sheet_path))
    p1 = pd.read_csv("~/extracted_eprime_AS_FWF/participants.tsv",
                     sep='\t').set_index("sub-ID")[["sheetpaths"]]

    allsheets = sorted(flatten([[join(maindir, row[0], file)
                                 for file in ls(join(maindir, row[0]))
                                 if file.endswith(".txt") and \
                                  bool(file.find("MACOSX") != -1)==False]
                                for row in p1.iterrows()]))
    
    allsheets = sorted([(bname(dname(sheet)), sheet) for sheet in allsheets])
    allsheetsdf = df(allsheets, columns=['sub-ID', 'sheetpath']).set_index('sub-ID')
    allsheetsdf['prefix'] = [bname(row[1]['sheetpath']).split(\
                                row[0][4:4+len(row[0].split("sub-")[1])])[0]
                             for row in allsheetsdf.iterrows()]
    

    return allsheetsdf

def main():
    allsheetsdf = NEW_get_allsheetsdf()

if __name__ == '__main__':
    main()
    