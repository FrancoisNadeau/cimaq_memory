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
from parsetxtfile import identify_fixed_width

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
        src.seek(0)
#         hdr = src.read(1) not in '.-0123456789'
#         if hdr:
#             hdr = 0
#         else:
#             hdr = False
#         nrows = len(lines4test)
        valuez = [bname(filename), dialect.delimiter, dialect.doublequote,
                  dialect.escapechar, dialect.lineterminator, dialect.quotechar,
                  dialect.quoting, dialect.skipinitialspace]
        cnames =['fname', 'has_header', 'sep',
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

def cleanup(test2, hdr):
    checkup = dupvalues(test2)
    while hdr:
        if checkup:
            test2 = fixbrokensheet(test2[1:]).inset(0, 'header', colnames)
        else:
            test2 = test2.inset(0, 'header', colnames)
        
    else:
        test2 = test2
    return test2

def listat(inds, inpt):
    '''
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    return itemgetter(*inds)(inpt)

def evenodd(inpt): 
    ''' 
    Source: https://www.geeksforgeeks.org/python-split-even-odd-elements-two-different-lists
    '''
    evelist = [ele[1] for ele in enumerate(inpt) if ele[0]%2 ==0] 
    oddlist = [ele[1] for ele in enumerate(inpt) if ele[0]%2 !=0]
    return evelist, oddlist  

def evenodd_col(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = listat(evlst, inpt), listat(odlst, inpt)
    return df(itemgetter(*evlst)(inpt)), df(itemgetter(*odlst)(inpt))

def evenodd_col2(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = listat(evlst, inpt), listat(odlst, inpt)    
    return df(evvals), df(odvals)
#     return itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)

def splitrows(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals = itemgetter(*evlst)(inpt)
    odvals = itemgetter(*odlst)(inpt)
    return evvals == odvals

def dupcols(inpt):
    '''
    Adapted from
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    doublevals = dupvalues(inpt)
    msk = df(doublevals, dtype='object')
    boolcols = [all(itm[1])
               for itm in msk.iteritems()]
    return msk.loc[:, boolcols]

def fixbrokensheet(inpt):
    inpt = df(inpt)
    eve, odd = evenodd_col(inpt)
    cnames = dupcols(df(inpt)).columns
    # Both doubles_even & doubles_odd are the same
    doubles_even = df(eve, dtype='object')[[itm[1] for itm in cnames if itm[0]]]
    doubles_odd = df(odd, dtype='object')[[itm[1] for itm in cnames if itm[0]]]
    singles_even = df(eve, dtype='object')[[itm[1] for itm in cnames if not itm[0]]]
    singles_odd = df(odd, dtype='object')[[itm[1] for itm in cnames if not itm[0]]]
    rescued = pd.concat([singles_even.dropna(axis=0),
                         singles_odd.dropna(axis=0)],
                        axis=1).T.drop_duplicates()
    final = pd.concat([doubles_even, rescued], axis=1)

# Works well
def dupvalues(inpt):
    '''
    Adapted from
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
#     try:
#         not dupindex(inpt)
#     except dupindex(inpt):
    evlst, odlst = evenodd_col2([itm[0] for itm
                                 in enumerate(inpt)])
    evvals = itemgetter(*[itm[1] for itm in
                          enumerate(evlst)])(inpt)
    odvals = itemgetter(*[itm[1] for itm in
                          enumerate(odlst)])(inpt)
#     check = tuple(zip(evvals, odvals))
    return df(evvals, dtype='object').values == df(odvals, dtype='object').values

# Works well
def get_doublerows(inpt):
    inpt = df(inpt)
    rowbreaks = [item[0] for item
                 in enumerate(inpt.iteritems())
                 if splitrows(item[1][1])]
    return rowbreaks
#     return inpt[list(itemgetter(*rowbreaks)(list(inpt.columns)))]

# def get_doublerows2(inpt):
#     rowbreaks = [item[0] for item
#                  in enumerate(inpt.iteritems())
#                  if splitrows2(item[1][1])]
#     return inpt[list(itemgetter(*rowbreaks)(list(inpt.columns)))]

def get_singlerows(inpt):
    rowbreaks = [item[0] for item
                 in enumerate(inpt.iteritems())
                 if not splitrows(item[1][1])]
    return inpt[list(itemgetter(*rowbreaks)(list(inpt.columns)))]

def get_singlerows2(inpt):
    rowbreaks = [item[0] for item
                 in enumerate(inpt.iteritems())
                 if not splitrows2(item[1][1])]
    return inpt[list(itemgetter(*rowbreaks)(list(inpt.columns)))]
    #     odvals = itemgetter(*odlst)(inpt)

#     return evlst, odlstdef splitrows2(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = oddeven([itm[0] for itm in enumerate(inpt)])
    evvals = itemgetter(*evlst)(inpt)
    odvals = itemgetter(*odlst)(inpt)
    return bool(pd.Series(evvals).values == pd.Series(odvals).values)
def splitrows2vals(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals = itemgetter(*evlst)(inpt)
    odvals = itemgetter(*odlst)(inpt)
    return evvals == odvals

def prepbytes(filename):
    rawsheet = open(filename , "rb")
    hdr = rawsheet.read(1) not in b'.-0123456789'
    rawsheet.seek(0)
    test = tuple(line for line in rawsheet.readlines())
    rawsheet.seek(0)
    test2 = df((pd.Series(line.split())
                for line in rawsheet.readlines()))
    dupindex = splitrows(test2[test2.columns[0]].values.tolist())
    nlines = len(test)
    rowbreaks = get_doublerows(test2)
    widths = pd.Series(len(line) for line in test)
    if hdr:
        colnames = test2.loc[0][:test2[1:].shape[1]]
        test, test2= test[1:], test2[1:]
        if dupindex:            
            colnames = test2[1:].loc[0][:test2[1:].shape[1]]
            test, test2 = test[1:], test2[1:]
    else:
        colnames = None
    width = widths.max()
    nfields = test2.shape[1]
    rawsheet.seek(0)
    detector = udet()
    for line in rawsheet.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    encoding = detector.result['encoding']
    rawsheet.seek(0)
    txttest = rawsheet.read().decode(encoding)
    dialect = csv.Sniffer().sniff(txttest)
    valuez = [bname(filename), hdr, dupindex, rowbreaks, width, nlines,
              nfields, colnames, encoding,
              dialect.delimiter, dialect.doublequote,
              dialect.escapechar, dialect.lineterminator, dialect.quotechar,
              dialect.quoting, dialect.skipinitialspace]
    cnames =['fname', 'has_header', 'dup_index', 'row_breaks', 'width',
             'n_lines', 'n_fields', 'colnames', 'encoding',
             'delimiter', 'doublequote', 'escapechar',
             'lineterminator', 'quotechar',
             'quoting', 'skipinitialspace']
    dialect_df = pd.Series(valuez, index=cnames)
    rawsheet.close()
    return dialect_df
bytesheets = [prepbytes(row[1]['fpath'])
              for row in infodf.iterrows()]

display(df(bytesheets))
# display(fixbrokensheet(infodf['prepsheets'][0]))
