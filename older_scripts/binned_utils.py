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
    sprtr = csv.Sniffer().sniff(test).delimiter
    if sprtr == ' ':
        sprtr = csv.Sniffer().sniff(str(test.replace('    ', '\t'))).delimiter
#     seprtr = str(withsep).split(str(cleaned))
    return sepin, sprtr

def get_values(filename):
    sheet = open(filename , "r", encoding=get_encoding(filename))
    sepin = [line.encode("ascii", "ignore").decode().strip()
               for line in sheet.readlines()]
    sprtr = csv.Sniffer().sniff(test).delimiter
    if sprtr == ' ':
        sprtr = csv.Sniffer().sniff(str(test.replace('    ', '\t'))).delimiter
#     seprtr = str(withsep).split(str(cleaned))
    return sepin, sprtr
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

#################################################################
############## - PART 2 -########################################

def check_header(filename, encod=None):
    '''
    Source: https://stackoverflow.com/questions/15670760/built-in-function-in-python-to-check-header-in-a-text-file
    '''
    if encod:
        encod = get_encoding(filename)
    sheet = open(filename, encoding=encod)
    first = sheet.read(1)
    sheet.close()
    return first not in '.-0123456789'

def get_header(filename):
    while check_header(filename):
        return pd.Series(getsep(filename)[0].strip().split()\
               [:len(get_values(filename)[-1])]).unique().tolist()
    
def get_nrows(filename, encod=None):
    if encod:
        encod = get_encoding(filename)
    sheet = open(filename , "r", encoding=encod)
    return len([line for line in sheet.readlines()])

def getsep(filename, encod=None):
    if not encod:
        sheet = open(filename , "r", encoding=encod)
    else: encod = get_encoding(filename)
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

def remake_sheets(filename, encod_type=None):
    sheet = open(filename, 'r', encoding=encod_type)
    for line in sheet.readlines():
        line = 
#     readf = io.open(fd, 'rb', buffering=0)
#         writef = io.open(fd, 'wb', buffering=0, closefd=False)
#         self.fileobj = io.BufferedRWPair(readf, writef)    
    for line in sheet.readlines():
        nline = line.encode(encod).decode('UTF-8')
        nsheet.append(nline)
    sheet.close()
    return nsheet

def loadpaths(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
#     cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    cimaq_dir = xpu(cimaq_dir)
    spaths = df(((sub, [itm for itm in sorted(loadimages(join(cimaq_dir,
                                              'extracted_eprimes2021', sub)))
                            if 'CIMAQ' in bname(itm) and '._' not in itm])
                  for sub in ls(join(cimaq_dir,
                                     'extracted_eprimes2021'))),
                columns=['subdccid', 'allpaths']).set_index('subdccid')
    prefixes = list(dict.fromkeys([bname(str(itm)).split("CIMAQ", 1)[0]
                                   for itm in flatten(spaths.values.tolist())
                                   if 'CIMAQ' in bname(itm) \
                                   and '._' not in itm]))
    prefixes = sorted(prefixes)
    spaths[prefixes] = [val[0] for val in spaths.values]
    spaths = spaths[prefixes]
    spaths['dccid'] = [ind.split('sub')[1] for ind in spaths.index]
    spaths['pscid'] = [bname(row[1][prefixes[0]]).split('_')[2]
                       for row in spaths.iterrows()]
    return spaths, prefixes

def detect_dialect_and_read(filename):
    """ Detect the dialect of a source and read it. """
    src = open(filename, 'r', encoding=get_encoding(filename))
    # Guess a suitable dialect by reading at most 1024 byte
    lesniff = csv.Sniffer()
    for line in src.readlin
    sample = src.read(4096)
    dialect = .sniff(sample)
#     diadict = {
#                'doublequote': dialect.doublequote,
#                'lineterminator': repr(dialect.lineterminator),
#                'quotechar': dialect.quotechar,
#                'skipinitialspace': dialect.skipinitialspace,     
#                'file_headers': csv.Sniffer().has_header(sample),
#                'encoding': get_encoding(filename)}
    # Reset the file cursor to the beginning of the file
#     src.seek(0)
    # Create a new reader object using the CSV dialect
#     nsheet = [newrow for newrow in csv.reader(src, diadict)]
    src.close()
    return nsheet

# BufferedRWPair(reader, writer, buffer_size=DEFAULT_BUFFER_SIZE)

def check_header(filename):
    ''' Source: https://stackoverflow.com/questions/15670760/built-in-function-in-python-to-check-header-in-a-text-file '''
    sheet = open(filename, encoding=get_encoding(filename))
    hashdr = sheet.read(1) not in '.-0123456789'
    sheet.close()
    return hashdr

def get_header(filename):
    if check_header(filename):
        return pd.Series(getsep(filename)[0].strip().split()\
                         [:len(get_values(filename)[-1])]).unique().tolist()

# Need get_values()
def get_nvalues(filename):
    return pd.Series(int(len(arow)) for arow in get_values(filename))

def get_colwidths(filename):
    return [np.round(itm[0]/itm[1]) for itm
            in tuple(zip(get_rowwidths(filename),
                         get_nvalues(filename)))]
def get_nrows(filename):
    sheet = open(filename , "r", encoding=get_encoding(filename))
    return len([line for line in sheet.readlines()])
def repr_values(filename):
    
#     src = open(filename, 'r', encoding=get_encoding(filename))
    # Guess a suitable dialect by reading at most 1024 byte
    
# def getsep(filename):
#     sheet = open(filename , 'r')
#     withsep = [''.join(filter(lambda x: x in set(line.printable), line))
#                for line in arch.readlines(archv.get_value())]
               
#                for line in sheet.readlines()] 
    seprtr = str(withsep).split(str(get_values(filename)))
    return seprtr, withsep

def get_rowwidths(filename):
    return [len(row) for row in getsep(filename)]

def zbase_infos(filename):
    with zipfile.ZipFile(filename, 'r') as archv:
        return vars(archv.testzip(name) for name in list(archv.nalelist()))
test = [zbase_infos(itm) for itm in loadimages('zeprimes.zip')]
# basereport = [zbase_infos(filename) for filename in loadima

def loadtxt(filename):
    return df(get_values(filename),
               columns=get_header(filename))

def parsingit(filename):
    return [len(arow.split(get_sep(filename)))
            for arow in getsep(filename)]


def get_colspecs(filename):
    withsep = getsep(filename)
    clean = get_values(filename)        
#     while check_headers(filename):        
    nrows = get_nrows(filename)
    headers = get_headers(filename)
    clean = get_values(filename)    
    nitms = pd.Series([len(trial) for trial in clean])
    itmsvec = [(nitms.min(), nitms.max()), (nitms[1].min(), nitms[1].max())]
    withsep = getsep(filename)
    width = pd.Series([len(trial) for trial in withsep])
    widthvec = [(width.min(), width.max()), (width[1].min(), width[1].max())]
#     test = np.arange(widthvec) * itmvec
    return (nrows, (itmsvec, widthvec))
#     if check_header == 0:
#         nitms, width = nitms[1:], width[1:]

def mystery(filename):
    withsep = getsep(filename)
    clean = get_values(filename)        
    width = pd.Series([len(trial) for trial in withsep])
    nrows = get_nrows(filename)
    testing = pandas.read_fwf(filename,
                              colspecs='infer', widths=None, infer_nrows=100, **kwds)

def get_values(filename):
    sheet = open(filename , "r", encoding=get_encoding())
    seprtr = get_sep(filename)
    if seprtr == ' ':
        seprtr = '\t'
        vals = [line.encode("ascii", "ignore").decode(get_encoding(filename)).strip().split(get_sep(filename))
                    for line in sheet.readlines()]
    else:
        vals = [line.encode("ascii", "ignore").decode(get_encoding(filename)).strip().split(get_sep(filename))
                    for line in sheet.readlines()]  
    if check_header(filename):
        vals = [arow[:len(vals[-1])] for arow in vals[1:]]
    return vals    
    sample = src.read(4096)
    dialect = csv.Sniffer().sniff(sample)
            
def getsep(filename):
    sheet = open(filename , 'r')
    withsep = [line.encode("ascii", "ignore").decode().strip()
               for line in sheet.readlines()]    
    seprtr = str(withsep).split(str(get_values(filename)))
    return seprtr, withsep
#     '''Source: https://www.kite.com/python/answers/how-to-redirect-print-output-to-a-variable-in-python
#     '''
#     old_stdout = sys.stdout
#     new_stdout = io.StringIO()
#     sys.stdout = new_stdout
#     printable
#     return new_stdout.getvalue()
#     withsep = [line.encode("ascii", "ignore").decode().strip()
#                for line in sheet.readlines()]


def swapit(filename):
    return df(get_values(files[0]
test = get_sep(files[0])
display(test)



def getsep(filename):
    sheet = open(filename , 'r')
    withsep = [line.encode("ascii", "ignore").decode().strip()
               for line in sheet.readlines()]    
    seprtr = str(withsep).split(str(get_values(filename)))
    return seprtr, withsep

def get_rowwidths(filename):
    return [len(row) for row in getsep(filename)]

def loadtxt(filename):
    return df(get_values(filename),
               columns=get_header(filename))

def parsingit(filename):
    return [len(arow.split(get_sep(filename)))
            for arow in getsep(filename)]

def get_colspecs(filename):
    withsep = getsep(filename)
    clean = get_values(filename)        
#     while check_headers(filename):        
    nrows = get_nrows(filename)
    headers = get_headers(filename)
    clean = get_values(filename)    
    nitms = pd.Series([len(trial) for trial in clean])
    itmsvec = [(nitms.min(), nitms.max()), (nitms[1].min(), nitms[1].max())]
    withsep = getsep(filename)
    width = pd.Series([len(trial) for trial in withsep])
    widthvec = [(width.min(), width.max()), (width[1].min(), width[1].max())]
#     test = np.arange(widthvec) * itmvec
    return (nrows, (itmsvec, widthvec))
#     if check_header == 0:
#         nitms, width = nitms[1:], width[1:]

def mystery(filename):
    withsep = getsep(filename)
    clean = get_values(filename)        
    width = pd.Series([len(trial) for trial in withsep])
    nrows = get_nrows(filename)
    testing = pandas.read_fwf(filename,
                              colspecs='infer', widths=None, infer_nrows=100, **kwds)
def detect_dialect_and_read(filename):
    """ Detect the dialect of a source and read it. """
    src = open(filename, 'r', encoding=get_encoding(filename))
    # Guess a suitable dialect by reading at most 1024 byte
    sample = src.read(4096)
    dialect = csv.Sniffer().sniff(sample)
    diadict = {'delimiter': get_sep(filename),
               'doublequote': dialect.doublequote,
               'lineterminator': repr(dialect.lineterminator),
               'quotechar': dialect.quotechar,
               'skipinitialspace': dialect.skipinitialspace,     
               'file_headers': csv.Sniffer().has_header(sample),
               'encoding': get_encoding(filename)}
    # Reset the file cursor to the beginning of the file
    src.seek(0)
    # Create a new reader object using the CSV dialect
    nsheet = [newrow for newrow in csv.reader(src, diadict)]
    src.close()
    return nsheet

def noduplicates(filename):
    aList=[]
    file = open(filename, 'r')
    reader = csv.reader(f, skipinitialspace=False,delimiter=',',
                        quoting=csv.QUOTE_NONE)
    reader = csv.reader(f, skipinitialspace=True,delimiter=',',
                        quoting=csv.QUOTE_NONE)        
    for row in reader:
        aList.append(row)
    return(aList)
        sprtr = csv.Sniffer().sniff(str(test.replace('    ', '\t'))).delimiter        
    return vals

def fetch_cimaq():
    cimaq_dir = '~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    datadir = 'CIMAQ_fmri_memory_data_neuromod_DATA/data'
    test = tuple((bname(dname(itm)), itm)
                  for itm in loadimages(join(xpu(cimaq_dir), datadir)))
    test2 = df((()))
    return test
test = fetch_cimaq()

def loadinfos(subject):
    meansheets = loadmeansheets()
    tmpidx = list(meansheets.sheets.behav.sort_index().index)
    subsheets = loadpaths()
    subsheets = subsheets.set_index('dccid', drop=False).loc[subject]
    subinfos = df(((row[0], row[1]['sheets'].loc[subject])
                   for row in meansheets.iterrows()),
                  columns=[subject, 'infos']).iloc[:3,].set_index(subject)
    test=subinfos
    return test

def clean_all_events(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
    cimaq_dir = xpu(cimaq_dir)
    frame, prefixes = loadpaths()
    enconsets = get_enc_onsets()
    encoutputs = get_enc_outputs()
    retsheets = get_ret_outputs()
    os.makedirs(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                           'data', 'events_memory'), exist_ok=True)
    os.makedirs(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                           'data', 'retrieval_memory'), exist_ok=True)
    sheetspersub = tuple(zip(frame.index, enconsets, encoutputs, retsheets))
    fullencsheets = [(join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                           'data', 'events_memory', frame.index[item[0]]+"_task-Memory_events.tsv"),
                      pd.concat([item[1][1][1], item[1][2][1]], axis=1,
                      sort=False).reset_index(\
                          drop=True))
                     for item in enumerate(sheetspersub)]
    p1 = pd.read_csv(join(xpu(cimaq_dir), 'meansheets',
                          'taskpaths_participants.tsv'),
                     sep='\t')[['pscid', 'dccid']]
    frame = pd.merge(frame, p1, on='dccid'
    frame['Encoding'] = [join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                              'data', 'events_memory',
                              str('sub'+str(row[1]['dccid'])+"_task-Memory_events.tsv"))
                         for row in frame.iterrows()]    
    frame['Retrieval'] = [join(cimaq_dir, 'CIMAQ_fmri_memory_data_neuromod_DATA',
                               'data', 'retrieval_memory',
                               str('sub'+str(row[1]['dccid'])+"_task-Retrieval_behavioural.tsv"))
                          for row in frame.iterrows()]
    [os.makedirs(dname(ndir), exist_ok=True) for ndir in tqdm(frame.Encoding)]
    retsvr = tuple(zip(frame.Retrieval, [itm[1] for itm in retsheets]))
    encsvr = tuple(zip(frame.Encoding, [itm[1] for itm in fullencsheets]))
    [itm[1].to_csv(itm[0], sep='\t') for itm in tqdm(retsvr)]
    [itm[1].to_csv(itm[0], sep='\t') for itm in tqdm(encsvr)]
    with open(join(cimaq_dir, 'cimaq_clean_unmerged.json'),
              'w', encoding='utf-8') as f:
        json.dump(np.array2string(np.array(sheetspersub, dtype='object')),
                  f, ensure_ascii=False, indent=0)
        f.close()

    frame = pd.merge(frame[['pscid', 'Encoding', 'Retrieval']],
                     p1[['pscid', 'dccid']], on='pscid', how='outer')
    frame.to_csv(join(cimaq_dir, 'meansheets', 'cimaq_paths.tsv'), sep='\t')
                     
def loadpaths(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
    cimaq_dir = xpu(cimaq_dir)
    spaths = df(((sub, [itm for itm in sorted(loadimages(join(cimaq_dir,
                                              'extracted_eprimes2021', sub)))
                            if 'CIMAQ' in bname(itm) and '._' not in itm])
                  for sub in ls(join(cimaq_dir,
                                     'extracted_eprimes2021')))).set_index(0)
    prefixes = list(dict.fromkeys([bname(str(itm)).split("CIMAQ", 1)[0]
                                   for itm in flatten(spaths.values.tolist())
                                   if 'CIMAQ' in bname(itm) \
                                   and '._' not in itm]))
    prefixes = sorted(prefixes)    
    spaths[prefixes] = [val[0] for val in spaths.values]
    spaths = spaths[prefixes]
    spaths['dccid'] = [int(ind.split('sub')[1]) for ind in spaths.index]
    spaths['pscid'] = [bname(row[1][prefixes[0]]).split('_')[2]
                       for row in spaths.iterrows()]
    return spaths, prefixes
                     
class participant():
    def __init__(self):
        self.name, self.subinfos, self.datas = loadinfos()
        self.enc_trials = pd.read_csv(self.subinfos.infos['taskpaths']['Encoding'],
                                  sep='\t').drop('Unnamed: 0', axis=1)
        self.retrieval = pd.read_csv(self.subinfos.infos['taskpaths']['Retrieval'],
                                     sep='\t').drop('Unnamed: 0', axis=1)
        self.confounds = pd.read_csv(self.subinfos.infos['meanMotion'],
                                     sep='\t')
#        Small adjustments
        self.retrieval['Spatial_RT'] = self.retrieval['Spatial_RT'].values/1000

        self.scan_infos = dict(nib.load(self.subinfos['paths']['func']).header)
        self.RepetitionTime = nib.load(self.subinfos['paths']['func']).header.get_zooms()[3]
        self.enc_trials['unscanned'] = self.enc_trials.trial_end >= self.RepetitionTime * \
                                                            self.scan_infos['dim'][4]
        self.enc_trials = self.enc_trials[['stimOnsetSec', 'stimDurSec', 'fixOnsetSec',
                                   'ImageID', 'tNumXcond', 'Condition',
                                   'CorrectSource', 'Stim_RT', 'trial_num', 'isi',
                                   'trial_end', 'unscanned', 'trialDur']]
        self.ctl_trials = self.enc_trials.where(self.enc_trials.Condition == 0).dropna()
        memsheet = pd.merge(self.enc_trials, self.retrieval, left_on='ImageID',
                        right_on='OldNumber').set_index('tNumXcond', drop=False)
        toscrub = memsheet.where(memsheet.unscanned).dropna()
        memsheet = memsheet.drop(toscrub.index)
 
        # Score calculation
        memsheet['category'] = memsheet['category'].replace({'OLD': 1, 'New':2})
        memsheet['recogAcc'] = memsheet.category == memsheet.Recognition_RESP

        memsheet['CorrectSource'] = [int(val) for val
                                     in memsheet.CorrectSource.values]
        memsheet['Spatial_RESP'] = [int(float(val)) for val
                                    in memsheet.Spatial_RESP.replace({'False': False})]
        memsheet['spaceAcc'] = memsheet.CorrectSource \
                               == memsheet.Spatial_RESP
        memsheet['hit'] = [row[1]['recogAcc'] and row[1]['spaceAcc'] == True \
                           and row[1]['recogAcc'] == True
                           for row in memsheet.iterrows()]
        memsheet['rejOk'] = [row[1]['recogAcc'] and row[1]['spaceAcc'] == True \
                             and row[1]['category'] == 'OLD'
                             for row in memsheet.iterrows()]
        memsheet['recogOkSrcMiss'] = [row[1]['recogAcc'] == True \
                                 and row[1]['spaceAcc'] == False \
                                 and row[1]['category'] == 'OLD'
                                 for row in memsheet.iterrows()]
        memsheet['miss'] = [row[1]['recogAcc'] or row[1]['spaceAcc']== False
                            for row in memsheet.iterrows()]
        memsheet['recogMissSrcOk'] = [row[1]['recogAcc'] == False
                                      and row[1]['spaceAcc'] == True
                                      for row in memsheet.iterrows()]
        self.enc_trials = memsheet[self.enc_trials.columns]
        self.enc_trials = self.enc_trials.rename(columns={'stimOnsetSec':'onset',
                                                  'trialDur': 'duration'})
        self.enc_trials['trial_type'] = np.ones(shape=self.enc_trials.shape[0],
                                                dtype=np.int8)
        self.ctl_trials = self.ctl_trials.rename(columns={'stimOnsetSec':'onset',
                                            'trialDur': 'duration'})
        memsheet = memsheet[['trial_num', 'hit', 'rejOk', 'recogOkSrcMiss',
                             'miss', 'recogMissSrcOk']]
        memsheet = memsheet.set_index('trial_num', drop=False)
        self.ret_outcomes = memsheet
        self.ctl_trials = self.ctl_trials.dropna().drop(['Condition'],
                                          axis=1)
        self.ctl_trials['trial_num'] = [int(tnum) for tnum
                                 in self.ctl_trials.trial_num]
        self.ctl_trials['trial_type'] = np.zeros(shape=self.ctl_trials.shape[0],
                                                 dtype=np.int8)
        self.enc_trials = self.enc_trials.set_index('trial_num').drop('Condition', axis=1)
        self.ctl_trials = self.ctl_trials.set_index('trial_num')
        self.ctl_trials['unscanned'] = self.ctl_trials['unscanned'].astype(bool)
        self.ctl_trials['CorrectSource'] = self.ctl_trials['CorrectSource'].astype(np.int8)
        self.events = pd.concat([self.enc_trials, self.ctl_trials])
        self.anat = nib.load(self.subinfos['paths']['anat'])
        self.func = nib.load(self.subinfos['paths']['func'])
        
 # Scoring
    memsheet['category'] = memsheet['category'].replace({'OLD': 1, 'New':2})
    memsheet['recogAcc'] = memsheet.category == memsheet.Recognition_RESP

    memsheet['CorrectSource'] = [int(val) for val
                                 in memsheet.CorrectSource.values]
    memsheet['Spatial_RESP'] = [int(float(val)) for val
                                in memsheet.Spatial_RESP.replace({'False': False})]
    memsheet['spaceAcc'] = memsheet.CorrectSource \
                           == memsheet.Spatial_RESP
    memsheet['hit'] = [row[1]['recogAcc'] and row[1]['spaceAcc'] == True \
                       and row[1]['recogAcc'] == True
                       for row in memsheet.iterrows()]
    memsheet['rejOk'] = [row[1]['recogAcc'] and row[1]['spaceAcc'] == True \
                         and row[1]['category'] == 'OLD'
                         for row in memsheet.iterrows()]
    memsheet['recogOkSrcMiss'] = [row[1]['recogAcc'] == True \
                             and row[1]['spaceAcc'] == False \
                             and row[1]['category'] == 'OLD'
                             for row in memsheet.iterrows()]
    memsheet['miss'] = [row[1]['recogAcc'] or row[1]['spaceAcc']== False
                        for row in memsheet.iterrows()]
    memsheet['recogMissSrcOk'] = [row[1]['recogAcc'] == False
                                  and row[1]['spaceAcc'] == True
                                  for row in memsheet.iterrows()]
    self.enc_trials = memsheet[self.enc_trials.columns]
    self.enc_trials = self.enc_trials.rename(columns={'stimOnsetSec':'onset',
                                              'trialDur': 'duration'})
    self.enc_trials['trial_type'] = np.ones(shape=self.enc_trials.shape[0],
                                            dtype=np.int8)
    self.ctl_trials = self.ctl_trials.rename(columns={'stimOnsetSec':'onset',
                                        'trialDur': 'duration'})
    memsheet = memsheet[['trial_num', 'hit', 'rejOk', 'recogOkSrcMiss',
                         'miss', 'recogMissSrcOk']]
    memsheet = memsheet.set_index('trial_num', drop=False)
    self.ret_outcomes = memsheet
    self.ctl_trials = self.ctl_trials.dropna().drop(['Condition'],
                                      axis=1)
    self.ctl_trials['trial_num'] = [int(tnum) for tnum
                             in self.ctl_trials.trial_num]
    self.ctl_trials['trial_type'] = np.zeros(shape=self.ctl_trials.shape[0],
                                             dtype=np.int8)
    self.enc_trials = self.enc_trials.set_index('trial_num').drop('Condition', axis=1)
    self.ctl_trials = self.ctl_trials.set_index('trial_num')
    self.ctl_trials['unscanned'] = self.ctl_trials['unscanned'].astype(bool)
    self.ctl_trials['CorrectSource'] = self.ctl_trials['CorrectSource'].astype(np.int8)
    self.events = pd.concat([self.enc_trials, self.ctl_trials])
    self.anat = nib.load(self.subinfos['paths']['anat'])
    self.func = nib.load(self.subinfos['paths']['func'])        

                     
def megamerge(dflist, merge_on, howto):
    return reduce(lambda x, y: pd.merge(x, y,
                                        on=merge_on,
                                        how=howto).astype('object'),
                  dflist)

def loadmeansheets():
    cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    failedQC = [str(ind) for ind in pd.read_csv(join(xpu(cimaq_dir),
                                'memoTask_ParticipantFile.tsv'),
                           sep='\t').dropna()[['dccid']].set_index('dccid').index]
    meansheets = df.from_dict(dict((bname(itm).split('_')[0],
                                    (itm, pd.read_csv(itm,
                                                      sep='\t', dtype='object').dropna()))
                                   for itm in sorted(loadimages(join(xpu(cimaq_dir),
                                                                     'meansheets')))),
                              orient='index', columns=['paths', 'sheets'])
    meansheets.sheets.meanMotion = meansheets.sheets.meanMotion.rename(
        columns={'total_scrubbed': 'total_scrubbed_frames'})
   # Check fMRI data availability per subject
    meansheets.sheets.bids['fMRI'] = meansheets.sheets.bids['fMRI'].replace(
        {'yes': True, not 'yes': False})
    meansheets.sheets.bids = meansheets.sheets.bids.where(
        meansheets.sheets.bids.fMRI == True)
    meansheets2 = megamerge([sheet.dropna() for sheet in meansheets.sheets],
                            merge_on = 'dccid', howto='inner')
    meansheets.sheets = [meansheets2[[col for col in sheet.columns
                                      if col in meansheets2.columns]].dropna().set_index('dccid')
                         for sheet in meansheets.sheets]
#     p1 = pd.read_csv(join(xpu(cimaq_dir), 'meansheets', 'taskpaths_participants.tsv'), sep='\t')
    return meansheets

def loadpaths(datadir='CIMAQ_fmri_memory_data_neuromod_DATA/data'):
    cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    cimaq_dir = xpu(cimaq_dir)
    test = pd.Series([bname(itm) for itm
                      in ls(join(xpu(cimaq_dir), datadir))]).unique()
    test2 = [itm for itm in loadimages(join(xpu(cimaq_dir), datadir))
             if 'sub' in itm]
    test3 = pd.Series([bname(itm).split('_')[1] for itm in test2]).unique()
    test4 = df([[[itm for itm in test2 if att in itm][0]
                 for sub in test3] for att in test],
               index=test, columns=test3).T
    test4['dccid'] = [ind.split('sub')[1] for ind in test4.index]
    return test4.dropna()

def makeindexes():
    meansheets = loadmeansheets()
    datas = loadpaths()
    mtmpindx = [itm for itm in loadmeansheets().sheets.behav.astype('object').index
                if itm in datas.dccid.values]
    return mtmpindx



def loadinfos2():
    meansheets = loadmeansheets()
#     datas = loadpaths()
#     mtmpindx = [itm for itm in loadmeansheets().sheets.behav.astype('object').index
#                 if itm in datas.dccid.values]
    datas = loadpaths()
    datas['subdccid'] = datas.index
    uindx = makeindexes()
    datas = datas.set_index('dccid', drop=False).loc[uindx]
    datas = datas.set_index('subdccid')
    subinfos = df(((subject, df(((row[0], row[1]['sheets'].loc[subject])
                     for row in meansheets.iterrows()),
                    columns=[subject, 'infos']).T) 
                     for subject in uindx),
                 columns=['dccid', 'mean_datas']).set_index('dccid')
#     return datas, subinfos
    return pd.merge(subinfos, datas, on='dccid').set_index('dccid')
                     