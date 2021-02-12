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
from removeEmptyFolders import removeEmptyFolders

def loadimages(impath='../images'):
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
    for allimages in os.walk(impath):
        for image in allimages[2]:
            impath = join(allimages[0], image)
            if os.path.isfile(impath):
                imlist.append(impath)
    return imlist

def flatten(nestedlst):
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
    flatlst = [bottomElem for sublist in nestedlst
               for bottomElem in (flatten(sublist)\
               if (isinstance(sublist, Sequence)\
               and not isinstance(sublist, str)) else [sublist])]
    return flatlst

def make_labels(datas, var_name):
    ''' Returns dict of (key, val) pairs using 'enumerate' on possible values 
        filtered by 'Counter' - can be used to map DataFrame objects - '''
    return dict(enumerate(Counter(datas[var_name]).keys(), start=1))

def loadfiles(indir=None, pathlist=None):
    if indir:
        spaths = loadimages(indir)
    else:
        spaths = pathlist         
    return df(((os.path.splitext(bname(sheet))[0],
                os.path.splitext(bname(sheet))[1],
                sheet) for sheet in spaths),
              columns=['fname', 'ext', 'fpaths'])

def sortmap(info_df, patterns):
    patterns = df(patterns, columns=['ids', 'patterns'])
    for row in patterns.iterrows():
        cmplr = re.compile(row[1]['patterns'])
        info_df[row[1]['ids']] = \
            [cmplr.search(row[1]['patterns']).group()
             in fname for fname in info_df.fname]
    return info_df

def regist_dialects(parsing_infos):
        [csv.register_dialect(
            row[1]['fpaths'], dialect = row[1] \
            [['delimiter', 'doublequote', 'escapechar',
              'lineterminator', 'quotechar', 'quoting',
              'skipinitialspace']])
         for row in parsing_infos.iterrows()]

def megamerge(dflist, howto, onto=None):
    return reduce(lambda x, y: pd.merge(x, y,
                                        on=onto,
                                        how=howto).astype('object'),
                  dflist)


def json_read(fpath):
    ''' Read JSON file to Python object.
        Parameter(s)
        -------------
        fpath:   str/path-like object (default='.' <cib_docs>)
        
        Reminder from native json module docs:
            JSON to Python conversion list
                JSON	PYTHON
                object*	dict    includes pandas DataFrame objects
                array	list
                string	str
                number (int)	int
                number (real)	float
                true	True
                false	False
                null	None
        Return
        ------
        Python object
    '''
    with open(fpath, "r") as read_file:
        return json.loads(json.load(read_file))

def json_write(jsonfit, fpath='.', idt=None):
    ''' Write JSON compatible python object to desired location on disk
        
        Parameters
        ----------
            jsonfit: JSON compatible object
                     Object to be written on disk.
                     See list below (from native JSON documentation)
            fpath:   str/path-like object (default='.' <cib_docs>)
                     Path where to save. All directories must exist.
                     Must end with '.json' file extension.
            idt:     Non-negative Int (default=None)
                     Indentation for visibility
                     *From native JSON docs: 
                         If ``indent`` is a non-negative integer,
                         then JSON array elements and object members
                         are pretty-printed with that indent level.
                         Indent level 0 only inserts newlines. 
                         ``None`` is the most compact representation.
                              
            JSON to Python conversion list
                JSON: PYTHON
                object*: dict    includes pandas DataFrame objects
                array: list
                string: str
                number (int)	int
                number (real)	float
                true: True
                false: False
                null: None
            
        Return
        ------
        None
    '''
    with open(join(dname(fpath), bname(fpath)), 'w') as outfile:
        json.dump(json.dumps(jsonfit, indent=idt), outfile)
        outfile.close()        

###############################################################################  
################## CIMA-Q SPECIDIC ############################################

def cimaqfilter(indir=join(xpu('~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/task_files/uzeprimes'))):
    ''' Removes all pratice files (and READMEs) 
        since no data was recorder due
        to response keyboard problems. Both READMEs indicate
        this sole information.
        Moves unused PDF files to "task_files/pdf_files"
    '''
    prfr = [file for file in loadimages(indir)
            if 'pratique' in bname(file)]
    pren = [file for file in loadimages(indir)
            if 'practice' in bname(file)]
    docxs = [file for file in loadimages(indir)
             if 'read_' in bname(file)]
    joinedlist = prfr + pren + docxs
    [os.remove(file) for file in joinedlist]
    os.makedirs(join(dname(indir), 'pdf_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'pdf_files', bname(file)))
     for file in loadimages(indir) if file.endswith('.pdf')]
    os.makedirs(join(dname(indir), 'edat2_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'edat2_files', bname(file)))
     for file in loadimages(indir) if file.endswith('.edat2')]
    os.makedirs(join(dname(indir), 'retrieval_log_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'retrieval_log_files', bname(file)))
     for file in loadimages(indir) if 'retrieval' in bname(file).split('_')[0]]
    os.makedirs(join(dname(indir), 'encoding_log_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'encoding_log_files', bname(file)))
     for file in loadimages(indir) if 'encoding' in bname(file).split('_')[0]]
    [os.remove(itm) for itm in loadimages(indir)
     if 'fuse_hidden0002f0fa00000022' in bname(itm)]
    [os.remove(itm) for itm in loadimages(indir)
     if bname(itm) == 'onset_event_encoding_cimaq_1234567_session1a.txt']
    [os.remove(itm) for itm in loadimages(indir)
     if bname(itm) == 'output_retrieval_cimaq_3589314_1.text.txt']
    [os.rename(itm, join(dname(itm), bname(itm).split('.')[0]+splitext(bname(itm))[1]))
     for itm in loadimages(indir) if splitext(bname(itm))[0].endswith(splitext(bname(itm))[0])]

