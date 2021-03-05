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
from os.path import join as pjoin
from os.path import splitext
from pandas import DataFrame as df
from tqdm import tqdm
from typing import Sequence
from typing import Union
from removeEmptyFolders import removeEmptyFolders
from json_read import json_read
from json_write import json_write
from sniffbytes import loadfiles
from sniffbytes import loadimages
from sniffbytes import repair_dataset

################## CIMA-Q SPECIDIC ############################################
def get_cimaq_dir_paths(cimaq_dir="~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives"):
    json_params = json_read(xpu('~/cimaq_memory/cimaq_dir_list.json'), 'r')
    dlst = df.from_dict(json_params['dir_list'], orient='index', columns=['suffixes'])
    patterns =  df.from_dict(json_params['patterns'], orient='index', columns=['patterns'])
    prefixes = pd.Series(json_params['prefixes'])
    dlst['fpaths'] = [pjoin(xpu(cimaq_dir), sfx) for sfx in dlst.suffixes]
    return dlst.T, patterns, prefixes

def repair_enc_task(cimaq_dir):
    onsets = loadfiles([fpath for fpath in 
                        loadimages(get_cimaq_dir_paths(cimaq_dir)[0].temp_events_dir.fpaths)
                        if 'onset_event' in bname(fpath)]).sort_values(
                            'fname').reset_index(drop = True)
    onsets[['pscid', 'dccid', 'subids']] = [(row[1].fname.split('_')[0],
                                             row[1].fname.split('_')[1],
                                             'sub-' + '-'.join(row[1].fname.split('_')[:2]))
                                  for row in onsets.iterrows()]
    outputs = loadfiles([fpath for fpath in 
                        loadimages(get_cimaq_dir_paths(cimaq_dir)[0].temp_events_dir.fpaths)
                        if 'output_responses' in bname(fpath)]).sort_values(
                            'fname').reset_index(drop = True)
    retrievals = loadfiles([fpath for fpath in 
                        loadimages(get_cimaq_dir_paths(cimaq_dir)[0].temp_events_dir.fpaths)
                        if 'output_retrieval' in bname(fpath)]).sort_values(
                            'fname').reset_index(drop = True)
    os.makedirs(get_cimaq_dir_paths(cimaq_dir)[0].events_dir.fpaths, exist_ok = True)
    os.makedirs(get_cimaq_dir_paths(cimaq_dir)[0].behavioral_dir.fpaths, exist_ok = True)

    for row in tqdm(onsets.iterrows(), desc = 'encoding_task'):
        pd.concat([pd.read_csv(onsets.iloc[row[0]].fpaths, sep = '\t', header = None).rename(
                   {0: 'trialnumber', 1: 'category',
                    2: 'trialcode', 3: 'oldnumber',
                    5: 'stim_onset', 6: 'stim_duration',
                    8: 'fix_onset', 9: 'fix_duration'},
                         axis = 1).drop([4, 7], axis = 1),
                  pd.read_csv(outputs.iloc[row[0]].fpaths, sep = '\t')[['correctsource', 'stim_rt']]],
                  axis = 1).to_csv(pjoin(get_cimaq_dir_paths(cimaq_dir)[0].events_dir.fpaths,
                                         'sub-'+'-'.join(bname(row[1].fpaths).split('_')[:2]) + \
                                                         '_task-encoding_events.tsv'), sep = '\t')
        pd.read_csv(retrievals.loc[row[0]].fpaths, header = 0, sep = '\t').iloc[:, :-1].to_csv(
                pjoin(get_cimaq_dir_paths(cimaq_dir)[0].behavioral_dir.fpaths,
                      'sub-'+'-'.join(bname(row[1].fpaths).split('_')[:2]) + \
                          '_task-retrieval_behavioral.tsv'), sep = '\t')
    shutil.rmtree(get_cimaq_dir_paths(cimaq_dir)[0].temp_events_dir.fpaths)
    return onsets[['pscid', 'dccid', 'subids']]

def fetch_cimaq(cimaq_dir):
    qc_ok = sorted([str(itm[0]) for itm in
                pd.read_csv(get_cimaq_dir_paths(
                    cimaq_dir)[0].mean_qc.fpaths, sep='\t').values])
    qc_ok
    to_exclude = df(sorted([(str(bname(itm).split('_')[0]),
                         str(bname(itm).split('_')[1]), itm) for itm in
                        loadimages(get_cimaq_dir_paths(
                            cimaq_dir)[0].zeprimes.fpaths)
                        if str(bname(itm).split('_')[1]) not in qc_ok]),
                   columns = ['pscid', 'dccid', 'fpaths']).set_index(
                       'dccid').sort_index().reset_index().fpaths.tolist()

    repair_dataset(get_cimaq_dir_paths(cimaq_dir)[0].zeprimes.fpaths,
                   get_cimaq_dir_paths(cimaq_dir)[0].temp_events_dir.fpaths,
                   exclude = ['pratique', 'practice', '.pdf', '.edat2'] + to_exclude)
    allids = repair_enc_task(cimaq_dir)
    pscids = allids.pscid
    dccids = allids.dccid
    subids = allids.subids
    cimaq = pd.concat([subids, pscids, dccids] + [loadfiles(loadimages(cimaqpath)).dropna(axis = 0)['fpaths']
                                  for cimaqpath in get_cimaq_dir_paths(cimaq_dir)[0].loc['fpaths'][1: 6]],
                      axis = 1).dropna(axis = 0).T.reset_index(drop = True).T
    cimaq = cimaq.rename(columns = {0: 'subid', 1: 'pscid', 2: 'dccid', 3: 'stereonl', 4: 'behavioral',
                                    5: 'confounds', 6: 'events', 7:'func'})
    return cimaq

