#!/usr/bin/env python3

###############################################################################
### Use to look at a set of sheets with identical values named differently. ###
###############################################################################

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
# get_infodf listat oddeven
from removeEmptyFolders import removeEmptyFolders
from parsetxtfile import get_avg_chars
from parsetxtfile import find_header
from cimaq_utils import *

def lowercols(sheets):
    '''
    Converts all columns's names to lowercase
    '''
    nsheets = []
    for sheet in sheets:
        sheet = sheet.rename(columns=dict(((col.lower, col)
                                          for col in sheet.columns)))
        nsheets.append(sheet)
    return nsheets

def findblind_cols(sheets, pattern):
    ''' 
    Returns boolean dataframe mask where values
    match a pattern despite differently named
    columns or items
    '''
    sheets = lowercols(sheets)
    sheets2 = [df(item[1].str.fullmatch(pattern)
                  for item in sheet.iteritems())
               for sheet in sheets]
    matched_cols = [sheet.loc[[row[0] for row
                               in sheet.iterrows()
                               if row[1].all()]].index.values.tolist()
                    for sheet in sheets2]
    return matched_cols

def check_ids(sheets, patterns):
    ''' 
    Parameters
    ----------
    sheets: Sequence of dataframes

    patterns: takes a tuple of 2 items
              tuples ('name', 'regex')
    Example: 
            patterns = (('dccid', '(?<!\d)\d{6}(?!\d)'),
                        ('pscid', '(?<!\d)\d{7}(?!\d)'))
    '''
    patterns = df(patterns, columns=['ids', 'patterns'])        
    return df((pd.Series((row[1]['ids'] in sheet.columns
                          for sheet in sheets), name=row[1]['ids'])
               for row in patterns.iterrows()))

def get_shortest_ind(sheets):
    ''' 
    Returns the shortest index values of a sequence
    of dataframes
    '''
    return next(sheet for sheet in sheets
                if sheet.shape[0] == \
                (pd.Series([sheet.shape[0]
                            for sheet in sheets]).min()))

# Very cool
def rename_imposter_cols(sheets, patterns):
    ''' 
    Renames duplicated columns with a common name
    by matching a regex pattern. Useful for data files
    from longitudinal studies wich could have been
    indexed or labeled differently.
        
    Renames common values with a common name
    '''
    patterns = df(patterns, columns=['ids', 'patterns'])    
    patterns['imposters'] = [findblind_cols(sheets, row[1]['patterns'])
                             for row in patterns.iterrows()]
    patterns['renamers'] = [[dict(zip(row[1]['imposters'][sheet[0]],
                                  [len(row[1]['imposters'][sheet[0]])*row[1]['ids']]))
                             for sheet in enumerate(sheets)]
                            for row in patterns.iterrows()]    
    for row in patterns.iterrows():
        sheets = [sheet[1].rename(columns=row[1]['renamers'][sheet[0]])
                  for sheet in enumerate(sheets)]
    return sheets
