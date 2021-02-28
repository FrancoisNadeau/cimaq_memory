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
from typing import Union
from removeEmptyFolders import removeEmptyFolders
from cimaq_utils import loadimages
from cimaq_utils import flatten

########### Miscellaneous '.txt' Files Parser #################################         

def get_dialect(filename, encoding:str=None):
    ''' Source: https://wellsr.com/python/introduction-to-csv-dialects-with-the-python-csv-module/#DialectDetection
        Description: Prints out all relevant formatting parameters of a dialect '''
    encoding = [encoding if encoding else get_bzip_enc(filename)][0]
    with open(filename, encoding=encoding) as src:
        dialect = csv.Sniffer().sniff(src.readline())
        src.seek(0)
#         lines4test = list(src.readlines())
        src.seek(0)
        valuez = [bname(filename), dialect.delimiter, dialect.doublequote,
                  dialect.escapechar, dialect.lineterminator,
                  dialect.quotechar, dialect.quoting, dialect.skipinitialspace]
        cnames =['fname', 'delimiter', 'doublequote', 'escapechar',
                 'lineterminator', 'quotechar', 'quoting', 'skipinitialspace']
        dialect_df = pd.Series(valuez, index=cnames)
        src.close()
        return dialect_df

def make_labels(datas, var_name):
    ''' Returns dict of (key, val) pairs using 'enumerate' on possible values
        filtered by 'Counter' - can be used to map DataFrame objects - '''
    return dict(enumerate(Counter(datas[var_name]).keys(), start=1))

def no_ascii(astring:str):
    '''
    Source: https://stackoverflow.com/questions/8689795/how-can-i-remove-non-ascii-characters-but-leave-periods-and-spaces-using-python
    '''
    return ''.join(filter(lambda x: x in set(string.printable), astring))

def letters(astring:str):
    '''
    Source: https://stackoverflow.com/questions/12400272/how-do-you-filter-a-string-to-only-contain-letters
    '''
    return ''.join([ch for ch in astring if character.isalpha()])

def num_only(astring:str):
    return ''.join(c for c in astring if c.isdigit())

def evenodd(inpt): 
    ''' 
    Source: https://www.geeksforgeeks.org/python-split-even-odd-elements-two-different-lists
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index

    '''
    eveseq = tuple(ele[1] for ele in enumerate(inpt) if ele[0]%2 ==0)
    oddseq = tuple(ele[1] for ele in enumerate(inpt) if ele[0]%2 !=0)
    return (eveseq, oddseq)

def splitrows(inpt):
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)
    return evvals == odvals

def evenodd_col2(inpt):
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = listat(evlst, inpt), listat(odlst, inpt)    
    return df(evvals), df(odvals)

def dupvalues(inpt): # Works well
    '''
    Adapted from
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    evlst, odlst = evenodd_col2([itm[0] for itm in enumerate(inpt)])
    evvals = itemgetter(*[itm[1] for itm in enumerate(evlst)])(inpt)
    odvals = itemgetter(*[itm[1] for itm in enumerate(odlst)])(inpt)
    return df(evvals, dtype='object').values == \
               df(odvals, dtype='object').values

###############################################################################

def get_doublerows(inpt:object)->list: # Works well
    return [itm[0] for itm in enumerate(df(inpt).iteritems())
            if splitrows(itm[1][1])]

def dupcols(inpt:object)->object:
    '''
    Adapted from
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    msk = df(dupvalues(inpt), dtype='object')
    boolcols = [all(itm[1]) for itm in msk.iteritems()]
    return msk.loc[:, boolcols]

def get_singlerows(inpt:object):
    rowbreaks = [item[0] for item in enumerate(inpt.iteritems())
                 if not splitrows(item[1][1])]
    return inpt[tuple(itemgetter(*rowbreaks)(tuple(inpt.columns)))]

def splitrows2vals(inpt):
#     inpt = [line[0] for line in inpt]
    evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
    evvals, odvals = itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)
    return evvals == odvals

def filter_lst_exc(exclude:Union[list, tuple], str_lst:Union[list, tuple],
                   sort:bool=False)->list:
    ''' https://www.geeksforgeeks.org/python-filter-list-of-strings-based-on-the-substring-list/ '''
    outlst = [itm for itm in str_lst if
              all(sub not in itm for sub in exclude)]
    return [sorted(outlst) if sort else outlst][0]

def filter_lst_inc(inclst:Union[list, tuple], str_lst:Union[list, tuple],
                   sort:bool=False)->list:
    ''' https://www.geeksforgeeks.org/python-filter-list-of-strings-based-on-the-substring-list/ '''
    outlst = [itm for itm in str_lst if any(sub in itm for sub in inclst)]
    return [sorted(outlst) if sort else outlst][0]
