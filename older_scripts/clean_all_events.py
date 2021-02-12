#!/usr/bin/env python

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
from chardet import detect
from chardet.universaldetector import UniversalDetector as udet
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from os.path import splitext
from pandas import DataFrame as df
from tqdm import tqdm
from cimaq_utils import flatten
from cimaq_utils import loadimages
from cimaq_utils import get_encoding

from fetch_cimaq_utils import loadpaths
from fetch_cimaq_utils import getid
from fetch_cimaq_utils import makename
from fetch_cimaq_utils import get_enc_onsets
from fetch_cimaq_utils import get_enc_outputs
from fetch_cimaq_utils import get_ret_outputs

def clean_all_events(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
    cimaq_dir = xpu(cimaq_dir)
    frame, prefixes = loadpaths()
    frame = frame.astype('object')
    enconsets = get_enc_onsets()
    encoutputs = get_enc_outputs()
    retsheets = get_ret_outputs()
    os.makedirs(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                           'data', 'events_memory'), exist_ok=True)
    os.makedirs(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                           'data', 'retrieval_memory'), exist_ok=True)
    sheetspersub = tuple(zip(frame.index, enconsets, encoutputs, retsheets))
    fullencsheets = [(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                           'data', 'events_memory',
                           frame.index[item[0]]+"_task-Memory_events.tsv"),
                      pd.concat([item[1][1][1], item[1][2][1]], axis=1,
                      sort=False).reset_index(\
                          drop=True))
                     for item in enumerate(sheetspersub)]
    frame['Encoding'] = [join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                              'data', 'events',
                              'events_'+row[0]+"_events.tsv")
                         for row in frame.iterrows()]    
    frame['Retrieval'] = [join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                               'data', 'behavioural',
                               'behav_'+row[0]+"_behavioural.tsv")
                          for row in frame.iterrows()]
    os.makedirs(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                              'data', 'events'), exist_ok=True)
    os.makedirs(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                              'data', 'retrieval'), exist_ok=True)
    retsvr = tuple(zip(frame.Retrieval, [itm[1] for itm in retsheets]))
    encsvr = tuple(zip(frame.Encoding, [itm[1] for itm in fullencsheets]))
    [itm[1].to_csv(itm[0], sep='\t', encoding=get_encoding(itm[0])) for itm in tqdm(retsvr)]
    [itm[1].to_csv(itm[0], sep='\t') for itm in tqdm(encsvr)]
    with open(join(cimaq_dir, 'cimaq_clean_unmerged.json'),
              'w', encoding='utf-8') as f:
        json.dump(np.array2string(np.array(sheetspersub, dtype='object')),
                  f, ensure_ascii=False, indent=0)
        f.close()
    frame.to_csv(join(cimaq_dir, 'meansheets', 'taskpaths_participants.tsv'), sep='\t')

def main():
    clean_all_events()

if __name__ == '__main__':
    main()
    