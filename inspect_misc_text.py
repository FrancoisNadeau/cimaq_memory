#!/usr/bin/env python3

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
from removeEmptyFolders import removeEmptyFolders
from cimaq_utils import loadimages
from cimaq_utils import flatten

########### Miscellaneous '.txt' Files Parser #################################         

def get_encoding(sheetpath):
    ''' Detect character encoding for files not encoded
        with default encoding type ('UTF-8').

    Parameters
    ----------
    sheetpath: Path or os.path-like objects pointing
               to a document file (various extensions supported,
               see online documentation at
               https://chardet.readthedocs.io/en/latest/

    Returns Pandas Series
        Ex: (index=["encoding", "confidence"], name="sheetname")
        "language" is dropped because it is known a priori to be Python
    '''
    detector, bsheet = udet(), open(sheetpath , "rb")
    for line in bsheet.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close(), bsheet.close()
    return detector.result['encoding']

def get_dialect(filename, encoding):
    ''' Source: https://wellsr.com/python/introduction-to-csv-dialects-with-the-python-csv-module/#DialectDetection
        Description: Prints out all relevant formatting parameters of a dialect '''
    with open(filename, encoding=encoding) as src:
        dialect = csv.Sniffer().sniff(src.readline())
        src.seek(0)
        lines4test = list(src.readlines())
        src.seek(0)
        valuez = [bname(filename), dialect.delimiter, dialect.doublequote,
                  dialect.escapechar, dialect.lineterminator, dialect.quotechar,
                  dialect.quoting, dialect.skipinitialspace]
        cnames =['fname', 'delimiter', 'doublequote', 'escapechar',
                 'lineterminator', 'quotechar', 'quoting', 'skipinitialspace']
        dialect_df = pd.Series(valuez, index=cnames)
        src.close()
        return dialect_df

def no_ascii(astring):
    '''
    Source: https://stackoverflow.com/questions/8689795/how-can-i-remove-non-ascii-characters-but-leave-periods-and-spaces-using-python
    '''
    return ''.join(filter(lambda x: x in set(string.printable), astring))

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

def evenodd_col2(inpt):
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = listat(evlst, inpt), listat(odlst, inpt)    
    return df(evvals), df(odvals)

def splitrows(inpt):
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)
    return evvals == odvals

def dupvalues(inpt): # Works well
    '''
    Adapted from
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    evlst, odlst = evenodd_col2([itm[0] for itm in enumerate(inpt)])
    evvals = itemgetter(*[itm[1] for itm in enumerate(evlst)])(inpt)
    odvals = itemgetter(*[itm[1] for itm in enumerate(odlst)])(inpt)
    return df(evvals, dtype='object').values == df(odvals, dtype='object').values

def get_doublerows(inpt): # Works well
    return [item[0] for item in enumerate(df(inpt).iteritems())
            if splitrows(item[1][1])]

def dupcols(inpt):
    '''
    Adapted from
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    msk = df(dupvalues(inpt), dtype='object')
    boolcols = [all(itm[1]) for itm in msk.iteritems()]
    return msk.loc[:, boolcols]

def get_singlerows(inpt):
    rowbreaks = [item[0] for item in enumerate(inpt.iteritems())
                 if not splitrows(item[1][1])]
    return inpt[tuple(itemgetter(*rowbreaks)(tuple(inpt.columns)))]

def splitrows2vals(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)
    return evvals == odvals

############################## TO TEST ##################################
# def get_compiler(inpt):
#     mrows = tuple(tuple(row[1].values.tolist())
#                   for row in inpt.dropna(axis=0, how='any').iterrows())
#     patterns = tuple(tuple(tuple('\W' if char.isalpha() else '\D'
#                 if char.isnumeric() else '\S' for char in str(item))
#                 for item in mrow) for mrow in mrows)
#     len_patterns = tuple(tuple(len(pattern) for pattern in
#                      flatten([[''.join(symbol for symbol in item)]
#                               for item in patrow]))
#                      for patrow in patterns)
#     patterns = df(tuple(tuple(pattern for pattern in
#                      flatten([[''.join(symbol for symbol in item)]
#                               for item in patrow]))
#                      for patrow in patterns))
#     check_maxrow = pd.Series((tuple(len(str(val)) for val in row[1].values))
#                              for row in patterns.iterrows()).max()
#     maxrow = pd.Series(tuple(patterns.loc[[row[0] for row in patterns.iterrows()
#                                  if tuple(len(str(val)) for val in row[1].values) == \
#                                            check_maxrow]].values.tolist())[0])
#     maxrow = pd.Series(tuple(letters(str(val)).split() for val in maxrow.values))
#     len_patterns = tuple(str({itm[1].min(), itm[1].max()})
#                          for itm in df(len_patterns).loc[maxrow.index].iteritems())
# #     assert patterns.shape == inpt.dropna(axis=0, how='any').shape
#     reg_row = tuple(zip(tuple('\\' + pd.Series(ch for ch in itm).unique().tolist()[0]
#                            for itm in maxrow), len_patterns))
#     reg_row = tuple(''.join(val for val in itm) for itm in reg_row)
#     return reg_row

# def parsebroken(inpt):
#     allvals = list(enumerate(inpt.iteritems()))
#     test = tuple(enumerate(tuple(itertools.chain.from_iterable(allvals))))
#     allcols = pd.Series([itm[1][1][0] for itm in test])
#     valsonly = [(itm[0], itm[1][1][1][1].values) for itm in enumerate(test)]
#     uvals = df([itm[1] for itm in valsonly]).drop_duplicates().T
#     colnames = allcols.loc[uvals.columns].to_dict()
#     uvals = uvals.rename(columns=colnames)
#     uvals = uvals.loc[sheets[-1].index]
#     return uvals

########## Unused #########################################################
# def cleanup(test2, hdr):
#     checkup = dupvalues(test2)
#     while hdr:
#         if checkup:
#             test2 = fixbrokensheet(test2[1:]).inset(0, 'header', colnames)
#         else:
#             test2 = test2.inset(0, 'header', colnames)    
#     else:
#         test2 = test2
#     return test2

# def get_encoding2(sheetlist):
#     ''' 
#     Short version of get_encoding using 'chardet.detect()'
#     instead of UniversalDectector
    
#     Detect character encoding for files not encoded
#     with current encoding type ('UTF-8').

#     Parameters
#     ----------
#     sheetlist: list of paths or os.path-like objects pointing
#                 to a document file (various extensions supported,
#                 see online documentation at
#                 https://chardet.readthedocs.io/en/latest/

#     Returns
#     -------
#     encodings: list of (sheet basename, encoding dict) tuples
#                 for each sheet in 'sheetlist'
#     '''
#     sheetlist = sorted(sheetlist)
#     results = []
#     for sheetpath in sheetlist:
#         bsheet = open(sheetpath, "rb").read()
#         rezz = chardet.detect(bsheet)
#         results.append(df.from_dict(rezz))
#     return results
