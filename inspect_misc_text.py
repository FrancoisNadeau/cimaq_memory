#!/usr/bin/env python3

###############################################################
########## Miscellaneous '.txt' file ##########################
########## Inspection Toolbox #################################

###############################################################
############ Get file encodings and sort accordingly ##########

import chardet
import collections
import csv
import glob
import gzip
import io
import itertools
import json
import lzma
import nibabel as nib
import nilearn
import numpy as np
import os
import pandas as pd
import pprint
import random
import re
import reprlib
import scipy
import shutil
import string
import sys
import tarfile
import xml.parsers.expat as xmlprse
import zipfile

from chardet import detect
from chardet.universaldetector import UniversalDetector as udet
from collections import Counter
from collections import OrderedDict
from functools import reduce
from io import StringIO
from matplotlib import pyplot as plt
from nilearn.plotting import plot_design_matrix
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn import image
from nilearn import plotting
from nilearn.plotting import plot_stat_map, plot_anat, plot_img, show
from numpy import nan as NaN
from operator import itemgetter 
from os import getcwd as cwd
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from os.path import splitext
from pandas import DataFrame as df
from tabulate import tabulate
from tqdm import tqdm
from typing import Sequence
# get_infodf listat oddeven
from removeEmptyFolders import removeEmptyFolders
from parsetxtfile import get_avg_chars
from parsetxtfile import find_header
from cimaq_utils import loadimages
from cimaq_utils import flatten

########### ZipFile Behaviour Control Toolbox #################################

cimaq_dir = xpu('~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives')
zeprimes = join(cimaq_dir, 'task_files/zipped_eprime')
uzeprimes = join(dname(zeprimes), 'uzeprimes')

def get_infodf(indir):
    encdf = get_clean_encodings(indir)
    diadf = df([get_dialect(row[1]['fpath'],
                            encoding=row[1]['encoding'])
                for row in encdf.iterrows()])
    return pd.merge(left=encdf, right=diadf,
                    on='fname', how='outer')

def clearnoencod(encdf):
#     encdf = get_all_encodings(indir=uzeprimes)
    nodet = encdf.loc[[row[1]['encoding'] == None
                      for row in encdf.iterrows()]]
    noenc = flatten([[itm for itm in list(encdf.fpath)
                      if splitext(fname)[0] in itm]
                     for fname in nodet.fname])
    [os.remove(fpath) for fpath in noenc]

def get_all_encodings(indir):  
    allfiles = [itm for itm in
                loadimages(indir)
                if not itm.startswith('.')]
    return df(tuple(zip([bname(itm) for itm in allfiles],
                        allfiles, [get_encoding(fname)
                                   for fname in allfiles])),
              columns=['fname', 'fpath', 'encoding'])

# def no_encod(encdf):
#     nodet = encdf.loc[[row[1]['encoding'] == None
#                       for row in encdf.iterrows()]]
#     return flatten([[itm for itm in list(encdf.fpath)
#                      if splitext(fname)[0] in itm]
#                     for fname in nodet.fname])

def get_clean_encodings(indir):
    encdf = get_all_encodings(indir)
    clearnoencod(encdf)
    encdf = get_all_encodings(indir)
    extlst = encdf.insert(loc=1, column='ext',
                          value=[splitext(fname)[1]
                                 for fname in encdf.fname])
    return encdf                    

def get_encoding(sheetpath):
    ''' 
    Detect character encoding for files not encoded
    with default encoding type ('UTF-8').

    Parameters
    ----------
    sheetpath: Path or os.path-like objects pointing
               to a document file (various extensions supported,
               see online documentation at
               https://chardet.readthedocs.io/en/latest/

    Returns
    -------
    results: Pandas 'Series'
        Ex: (index=["encoding", "confidence"], name="sheetname")
    "language" is dropped because it is known a priori to be Python
    '''
    detector = udet()
    bsheet = open(sheetpath , "rb")
    for line in bsheet.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    bsheet.close()
    return detector.result['encoding']

def get_encoding2(sheetlist):
    ''' 
    Short version of get_encoding using 'chardet.detect()'
    instead of UniversalDectector
    
    Detect character encoding for files not encoded
    with current encoding type ('UTF-8').

    Parameters
    ----------
    sheetlist: list of paths or os.path-like objects pointing
                to a document file (various extensions supported,
                see online documentation at
                https://chardet.readthedocs.io/en/latest/

    Returns
    -------
    encodings: list of (sheet basename, encoding dict) tuples
                for each sheet in 'sheetlist'
    '''
    sheetlist = sorted(sheetlist)
    results = []
    for sheetpath in sheetlist:
        bsheet = open(sheetpath, "rb").read()
        rezz = chardet.detect(bsheet)
        results.append(df.from_dict(rezz))
    return results

def get_dialect(filename, encoding):
    '''
    Source: https://wellsr.com/python/introduction-to-csv-dialects-with-the-python-csv-module/#DialectDetection
        - hdr variable replaces csv.Sniffer().has_header, which wouldn't work everytime
        Source: https://stackoverflow.com/questions/15670760/built-in-function-in-python-to-check-header-in-a-text-file
    Description: Prints out all relevant formatting parameters of a dialect
    '''
    with open(filename, encoding=encoding) as src:
        dialect = csv.Sniffer().sniff(src.readline())
        src.seek(0)
        lines4test = list(src.readlines())
        hdr = src.read(1) not in '.-0123456789'
#         hdr_check = tuple(enumerate(lines4test))
#         try:
            
#         except not hdr:
#             hdr = pd.Series([itm[1][0] in itm[0] for itm in hdf_check])
#         try:
#             hdr1 = csv.Sniffer().has_header([line.split() for line in src.readline()])
#         except Error:
#             hdr1 = None
#         try:
#             hdr = not csv.Sniffer().has_header(src.read(512))
#         except:
#             #Error("Could not determine delimiter"):
#             hdr = src.read(1024) not in '.-0123456789'
#         except hdr:
#             hdr = evenodd_col2(src)[0].read(1) not in '.-0123456789'
            
#         hdr2 = csv.Sniffer().has_header(src.read(1))          
#         hdr = bool(hdr1 or hdr2)
        if hdr:
            hdr = 0
        else:
            hdr = False
        nrows = len(lines4test)
        valuez = [bname(filename), hdr, dialect.delimiter,
                  nrows, dialect.doublequote, dialect.escapechar,
                  dialect.lineterminator, dialect.quotechar,
                  dialect.quoting, dialect.skipinitialspace]
        cnames =['fname', 'has_header', 'sep', 'n_rows',
                 'doublequote', 'escapechar',
                 'lineterminator', 'quotechar',
                 'quoting', 'skipinitialspace']
        dialect_df = pd.Series(valuez, index=cnames)
        src.close()
        return dialect_df

def no_ascii(astring):
    '''
    Source: https://stackoverflow.com/questions/8689795/how-can-i-remove-non-ascii-characters-but-leave-periods-and-spaces-using-python
    '''
    return ''.join(filter(lambda x: x
                          in set(string.printable),
                          astring))

def letters(instring):
    '''
        Source: https://stackoverflow.com/questions/12400272/how-do-you-filter-a-string-to-only-contain-letters
    '''
    valids = []
    for character in instring:
        if character.isalpha():
            valids.append(character)
    return ''.join(valids)

def num_only(astring):
    return ''.join(c for c in astring if c.isdigit())
