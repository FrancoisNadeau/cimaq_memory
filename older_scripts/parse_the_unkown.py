#!/usr/bin/env python

import csv
import glob
import json
import nibabel as nib
import nilearn
import numpy as np
import os
import pandas as pd
import pprint
import random
import re
import scipy
import sys
import zipfile

from collections import Counter
from functools import reduce
from matplotlib import pyplot as plt
from nilearn.plotting import plot_design_matrix
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn import image
from nilearn import plotting
from nilearn.plotting import plot_stat_map, plot_anat, plot_img, show
from numpy import nan as NaN
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df

from cimaq_utils import flatten
from cimaq_utils import get_encoding
from cimaq_utils import loadimages

from loading_utils import megamerge
from loading_utils import loadmeansheets
from loading_utils import loadpaths
from loading_utils import makeindexes
from loading_utils import loadinfos2

from chardet.universaldetector import UniversalDetector as udet

def check_header(filename):
    '''
    Source: https://stackoverflow.com/questions/15670760/built-in-function-in-python-to-check-header-in-a-text-file
    '''
    with open(filename, encoding=get_encoding(filename)) as f:
        first = f.read(1)
        return first not in '.-0123456789'

def get_header(filename):
    while check_header(filename):
        return pd.Series(getsep(filename)[0].strip().split()\
                         [:len(get_values(filename)[-1])]).unique().tolist()

    
def get_nrows(filename):
    sheet = open(filename , "r", encoding=get_encoding(filename))
    return len([line for line in sheet.readlines()])

def getsep(filename):
    sheet = open(filename , "r", encoding=get_encoding(filename))
    sepin = [line.encode("ascii", "ignore").decode().strip()
               for line in sheet.readlines()]    
#     seprtr = str(withsep).split(str(cleaned))
    return sepin

def get_values(filename):
    sheet = open(filename , "r", encoding=get_encoding(filename))
    vals = [line.encode("ascii",
                        "ignore").decode().strip().split(get_sep(filename))
                for line in sheet.readlines()]  
    if check_header(filename):
        vals = [arow[:len(vals[-1])] for arow in vals[1:]]
    return vals

def get_nvalues(filename):
    return pd.Series(int(len(arow)) for arow in get_values(filename))
    
def get_rowwidths(filename):
    return [len(row) for row in getsep(filename)]

def get_colwidths(filename):
    return [np.round(itm[0]/itm[1]) for itm
            in tuple(zip(get_rowwidths(filename),
                         get_nvalues(filename)))]

def get_encoding(sheetpath):
    detector = udet()
    bsheet = open(sheetpath , "rb")
    for line in bsheet.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    return detector.result['encoding']

def fixbroken(filename1, filename2):
    sheet1 = pandas.read_fwf(filename1, colspecs='infer',
                             widths=None, infer_nrows=100, **kwds)

def get_sep(filename):
    test = getsep(filename)[0]
    sprtr = csv.Sniffer().sniff(test).delimiter
    if sprtr == ' ':
        sprtr = csv.Sniffer().sniff(str(test.replace('    ', '\t'))).delimiter
    return sprtr            

def noduplicates(filename):
    df(get_values(filename)).drop_duplicates(keep=False)
    uindx = pd.Series((atrow[0] for atrow in get_values(filename))).unique().tolist()
    allindx = [arow[0] for arow in get_values(filename)]
    return uindx, allindx

def loadtxt(filename):
    return df(get_values(filename),
               columns=get_header(filename))

def parsingit(filename):
    return [len(arow.split(get_sep(filename)))
            for arow in getsep(filename)]
