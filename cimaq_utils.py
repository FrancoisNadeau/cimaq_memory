#!/usr/bin/env python3

"""
Created on Thu Nov  5 22:55:43 2020

@author: francois
"""

import chardet
import collections
import csv
import glob
import io
import itertools
import json
import numpy as np
import os
import pandas as pd
import random
import re
import reprlib
import shutil
import string
import sys

from chardet import detect
from chardet.universaldetector import UniversalDetector as udet
from collections import Counter
from collections import OrderedDict
from functools import reduce
from io import StringIO
from matplotlib import pyplot as plt
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
from tqdm import tqdm
from typing import Sequence
from typing import Union
from removeEmptyFolders import removeEmptyFolders
from json_read import json_read
from json_write import json_write

def loadimages(indir:Union[os.PathLike, str])->list:
    '''
    Description
    -----------
    Lists the full relative path of all '.jpeg' files in a directory.
    Only lists files, not directories.

    Parameters
    ----------
    imdir: type = str
        Name of the directory containing the images.

    Return
    ------
    imlist: type = list
        1D list containing all '.jpeg' files' full relative paths
    '''
    imlist = []
    for allimages in os.walk(indir):
        for image in allimages[2]:
            indir = join(allimages[0], image)
            if os.path.isfile(indir):
                imlist.append(indir)
    return imlist

def flatten(nested_seq):
    """
    Description
    -----------
    Returns unidimensional list from nested list using list comprehension.

    Parameters
    ----------
        nestedlst: list containing other lists etc.

    Variables
    ---------
        bottomElem: type = str
        sublist: type = list

    Return
    ------
        flatlst: unidimensional list
    """
    return [bottomElem for sublist in nested_seq
            for bottomElem in (flatten(sublist)\
                               if (isinstance(sublist, Sequence)\
                                   and not isinstance(sublist, str))
                               else [sublist])]

def loadfiles(pathlist:Union[list, tuple])->object:
    return df(((os.path.splitext(bname(sheet))[0],
                os.path.splitext(bname(sheet))[1],
                sheet) for sheet in pathlist),
              columns=['fname', 'ext', 'fpaths']).sort_values(
                  'fname').reset_index(drop=True)

def sortmap(info_df:object, patterns:object)->object:
    ''' Identifies files in info_df with boolean values
        True: Pattern is in filename; False: It is not'''
    patterns = df(patterns, columns=['ids', 'patterns'])
    for row in patterns.iterrows():
        cmplr = re.compile(row[1]['patterns'])
        info_df[row[1]['ids']] = \
            [cmplr.search(row[1]['patterns']).group()
             in fname for fname in info_df.fname]
    return info_df

def find_key(input_dict:dict, value):
    ''' Source: https://stackoverflow.com/questions/16588328/return-key-by-value-in-dictionary '''
    return next((k for k, v in input_dict.items() if v == value), None)

def megamerge(dflist, howto, onto=None):
    return reduce(lambda x, y: pd.merge(x, y,
                                        on=onto,
                                        how=howto).astype('object'),
                  dflist)

################## CIMA-Q SPECIDIC ############################################
def get_cimaq_dir_paths(cimaq_dir="~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives"):
    json_params = json_read(xpu('~/cimaq_memory/cimaq_dir_list.json'), 'r')
    dlst = df.from_dict(json_params['dir_list'], orient='index', columns=['suffixes'])
    patterns =  df.from_dict(json_params['patterns'], orient='index', columns=['patterns'])
    prefixes = pd.Series(json_params['prefixes'])
    dlst['fpaths'] = [join(xpu(cimaq_dir), sfx) for sfx in dlst.suffixes]
    return dlst.T, patterns, prefixes
