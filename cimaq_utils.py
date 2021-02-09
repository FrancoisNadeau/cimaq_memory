#!/usr/bin/env python3

"""
Created on Thu Nov  5 22:55:43 2020

@author: francois
"""

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

cimaq_dir = xpu('~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives')
zeprimes = join(cimaq_dir, 'task_files/zipped_eprime')
uzeprimes = join(dname(zeprimes), 'uzeprimes')
taskdir= xpu('~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants')

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


def loadfiles(indir):
    return df(((os.path.splitext(bname(sheet))[0],
                os.path.splitext(bname(sheet))[1],
                sheet) for sheet
               in loadimages(indir)),
              columns=['fnames', 'ext', 'fpaths'])

def regist_dialects(parsing_infos):
        [csv.register_dialect(row[1]['fpaths'],
                             dialect = row[1][['delimiter', 'doublequote', 'escapechar',
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

def absoluteFilePaths(maindir):
    for allthings in os.walk(maindir):
        for folder in allthings[1]:
            yield os.path.abspath(os.path.join(dirpath, f))

def emptydir(folder = '/path/to/folder'):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


###############################################################################  
###################################
##### CIMA-Q SPECIDIC ############

def sortmap(cimaqdf):
    prefixes = pd.Series(('_'.join(val.split('_')[:2])
                          for val in cimaqdf.fname)).unique()
    cimaqdf[prefixes] = [[pref in row[1]['fname']
                          for pref in prefixes]
                         for row in cimaqdf.iterrows()]
    pscid_ = re.compile('\d{7}')
#     cimaqdf = get_prefixes(infodf)
    cimaqdf['pscid'] = [pscid_.search(fname).group()
                        for fname in cimaqdf.fname]
    return cimaqdf

def loadscans(folderlist=[join(dname(taskdir), 'anat'),
                          join(dname(taskdir), 'confounds'),
                          join(dname(taskdir), 'fmri')]):
    cmplr = re.compile('\d{6}')
    scans = df((loadimages(folder)
              for folder in folderlist),
             index = [bname(folder)
                      for folder in folderlist])    
    scans = scans.rename(
               columns=dict(((scan[0], cmplr.search(bname(scan[1])).group())
                                 for scan in enumerate(scans.iloc[0])))).T
    scans.index.names = ['dccid']
    scans.index = pd.to_numeric(scans.index)
    scans = scans.reset_index(drop=False)
    scans = scans.convert_dtypes()
    return scans

def cimaqfilter(indir=uzeprimes):
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

####################################
####### Less Important Below #######

def prepms(sheetnames):
    for sheet in sheetnames['sheetvalues']:
        if 'participant_id' in list(sheet.columns):
            sheet = sheet.rename(columns={'participant_id': 'dccid'})
        if 'id' in list(sheet.columns):
            sheet = sheet.rename(columns={'id': 'dccid'})        
        if 'dccid' in list(sheet.columns):
            sheet['dccid'] = sheet['dccid']
        if 'sub_ids' in list(sheet.columns):
            sheet = sheet.rename(columns={'sub_ids': 'dccid'})        
        sheet.columns = map(str.lower, sheet.columns)
        sheet.columns = map(str.strip, sheet.columns)        
#         sheet = sheet.set_index(list(sheet.columns)[0]).sort_index()
        sheet = sheet.reindex(sorted(sheet.columns), axis=1).dropna()
    return sheetnames

def mkvsheet(sheetnames):
    meansheets = [sheet for sheet in
                  sheetnames['sheetvalues']]
    l1 = [sheet.dropna() for sheet in meansheets
          if 'dccid' in list(sheet.columns)]
    l2 = [sheet.dropna() for sheet in meansheets
          if 'pscid' in list(sheet.columns)]
    l1df = megamerge(l1, 'outer', onto='dccid')
    l2df = megamerge(l2, 'outer', onto='dccid') 
    l3df = pd.merge(l1df, l2df, how='outer',
                    left_on='pscid_y', right_on='pscid_y')
    colsorder = pd.Series(l3df.columns)
    l3df = l3df.T.drop_duplicates(keep='first').T
    ncols = [col.replace('_x', '')
             for col in l3df.columns
              if '_x' or '_y' in col]
    l3df.columns = ncols
    l3df = l3df.dropna()
    l3df['dccid'] = [int(str(itm).split('.')[0]) for itm in l3df.dccid]
    l3df['pscid'] = [int(str(itm).split('.')[0]) for itm in l3df.pscid]
    l3df.to_csv(join(cimaq_dir, 'task_files',
                     'mean_vectors.tsv'), sep='\t')
    return l3df

def mkmeansheet(indir= '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants',
                snames = ['Neuropsych/ALL_Neuropsych_scores.tsv',
                             'MotionResults/fMRI_meanMotion.tsv',
                             'TaskResults/fMRI_behavMemoScores.tsv',
                             'MemoTaskParticipantFile.tsv',
                             'Participants_bids.tsv',
                             'Splitting_list.tsv']):

    meansheet = mkvsheet(prepms(loadsheets(snames,
                                           xpu(indir)).dropna()))
    meansheet['pscid'] = [str(itm).split('.')[0]
                          for itm in meansheet.pscid]
    meansheet['dccid'] = [str(itm).split('.')[0]
                          for itm in meansheet.dccid]
    qcok = pd.read_csv(join(indir, 'sub_list_TaskQC.tsv'),
                       sep='\t').values.tolist()
    qcok = [ind for ind in qcok if ind in list(meansheet.dccid)]
    meansheet = meansheet.loc[[meansheet.dccid in qcok]]
    return meansheet.drop(columns=['pscid_y'])
    
############################
###### Broken ##############

# def get_meansheet(sdir='/media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants'):
#     snames = ['Participants_bids.tsv',
#               'MemoTaskParticipantFile.tsv',
#               'TaskResults/fMRI_behavMemoScores.tsv',
#               'Neuropsych/ALL_Neuropsych_scores.tsv',
#               'MotionResults/fMRI_meanMotion.tsv',
#               'sub_list_TaskQC.tsv']
#     constant_dir = xpu('~/../..')
#     spaths = [join(constant_dir, sdir, sname)
#               for sname in snames]
#     encs = [get_encoding(spath) for spath in spaths]
#     infos = df(tuple(zip(spaths, encs)))
#     sheets = [pd.read_csv(row[1][0], encoding=row[1][1], sep='\t')
#               for row in infos.iterrows()]
#     allvals = [list(enumerate([itm[1].sort_values() for itm in sheet.iteritems()]))
#                for sheet in sheets]
#     test = tuple(enumerate(tuple(itertools.chain.from_iterable(allvals))))
#     allcols = pd.Series([itm[1][1][0] for itm in test])
#     valsonly = [(itm[0], itm[1][1][1][1]) for itm in enumerate(test)]
#     uvals = df([itm for itm in enumerate(valsonly)]).drop_duplicates().T
#     colnames = allcols.loc[uvals.columns].to_dict()
#     uvals = uvals.rename(columns=colnames)
#     uvals = uvals.loc[sheets[-1].index]
#     uvals.columns = map(str.lower, uvals.columns)
#     return uvals

# uvals = get_meansheet().convert_dtypes().drop_duplicates().T

# def splitmerge(inpt):
#     evlst, odlst = evenodd([itm[0] for itm in inpt])
#     evvals = itemgetter(*[itm[0] for itm in
#                           enumerate(evlst)])(inpt)
#     odvals = itemgetter(*[itm[0] for itm in
#                           enumerate(odlst)])(inpt)
# #     evelst, oddlst = Split([line[0] for line in inpt])
#     hdr = bytearray(str(inpt[0]), 'utf8').decode() not in '.-0123456789'
#     cnames=None
#     if hdr == True:
# #         hdr = 0
# #         evlst, odlst = evlst[1:], odlst[1:]
#         evvals, odvals = evvals[1:], odvals[1:]
# #         cnames = pd.Series(evvals[0] + odvals[0]).unique().tolist()
#         cnames = evvals[0]
#     else: evvals, odvals, cnames = evvals, odvals, cnames 
#     if evlst == odlst:
#         try:
#             evdfl = df(enumerate(evvals), columns=cnames).drop_duplicates(keep='last')
#             evdfn = df(enumerate(evvals), columns=cnames).drop_duplicates(keep=False)
# #             oddff = df(odvals, columns=cnames).drop_duplicates(keep='first')
#             oddfl = df(enumerate(odvals), columns=cnames).drop_duplicates(keep='last')
#             oddfn = df(enumerate(odvals), columns=cnames).drop_duplicates(keep=False)
#             outpt = megamerge([evdfl, evdfn, oddfl, oddfn], howto='outer', onto=cnames)
#         except ValueError:
            
#             outpt = df(inpt).pad()
# #             outpt =  df(enumerate([[''.join([itm for itm in line
# #                                     if ' ' not in itm]).strip('\n').replace('nnn', ',').replace('nn', ',')]
# #                          for line in inpt]))
# #         return evdf, oddf
# #         return megamerge([evdff, oddfl, evdfl, oddff], howto='outer', onto=cnames)
# #         df1 = pd.merge(evdf, oddf)
# #         return df1
# #         df2 = pd.merge(evdf, oddf).drop_duplicates(keep='last')
# #         return pd.merge(df1, df2, on=0, sort=True)
#     else:
# #         outpt = pd.read_fwf(np.array(inpt), header=None)
#         outpt = df(inpt)
# #         outpt = df(pd.Series(enumerate(inpt)).unique()).dropna(axis=1, how='all')
#     return outpt

# def prepstr(filename, encoding, hdr, sep):
#     sheet = open(filename , "r", encoding=encoding)
# #     if sep != '\t':
# #         nsep = '\t'
#     sep = csv.Sniffer().sniff(sheet.readline()).delimiter    
#     test = []
#     test2 = []
#     test3 = []
# #     widths = []
#     widths = []
# #     hdr = bytearray(str(sheet[0]), 'utf8').decode() not in '.-0123456789'

#     nitems = []
#     for line in sheet.readlines():
#         line = no_ascii(line)
# #         line = line.replace('    ', ' ')
# #         line = line.replace(' . ', ' n\a ')
# #         line = line.lstrip()
# #         line = line.rstrip()
# #         line = line.strip('    ')
# #         line = line.replace('    ', ' ')
#         line = line.strip().replace(sep, '\t').replace(' ', '_')
# #         line = no_ascii(line)
#         widths.append(len(line.encode(encoding)))
#         line = line.ljust(len(line)).strip()
#         line = line.rjust(len(line)).strip()
# #         line = line.strip('n')
#         line = line.split()
#         line2 = sep.join(itm for itm in line).strip().lstrip().rstrip()
# #         line2 = line.ljust(len(line)).strip()
# #         line2 = line.rjust(len(line)).strip()        
#         test.append(line)
#         line2 = line2.strip().split()
#         test2.append(line2)
#         line3 = line2.strip()
#         nitems.append(len(line2))
#     nitems = pd.Series(nitems).max()
#     nrows = len(test2)
#     maxwidth = pd.Series(widths).max
#     if hdr:
#         width = pd.Series(widths[1:]).max()
#         nitems = pd.Series(nitems[1:]).max()
#         test = [line[:width] for line in test[1:]]
#         colnames = test2[0][:nitems]
#         nrows = len(test2[1:])
    

# #         test = [line[:width] for line in test]
# #         ncol.append(line.count(sep))
#     test2 = [line[:nitems] for line in test2]

#     sheet.close()
#     return test3

# def prepbytes(filename, encoding, hdr, sep):
#     sheet = open(filename , "r", encoding=encoding)
# #     if sep != '\t':
# #         nsep = '\t'
# #     sep = csv.Sniffer().sniff(sheet.readline()).delimiter    
#     test = []
#     test2 = []
# #     widths = []
#     widths = []
# #     hdr = bytearray(str(sheet[0]), 'utf8').decode() not in '.-0123456789'
#     nitems = []
#     for line in sheet.readlines():
#         line = no_ascii(line)
# #         line = line.replace('    ', ' ')
# #         line = line.replace(' . ', ' n\a ')
# #         line = line.lstrip()
# #         line = line.rstrip()
# #         line = line.strip('    ')
# #         line = line.replace('    ', ' ')
#         line = line.strip().replace(sep, '\t').replace(' ', '_')
# #         line = no_ascii(line)
#         widths.append(len(line.encode(encoding)))
#         line = line.ljust(len(line)).strip()
#         line = line.rjust(len(line)).strip()
# #         line = line.strip('n')
#         line = line.split()
#         line2 = sep.join(itm for itm in line).strip().lstrip().rstrip()
# #         line2 = line.ljust(len(line)).strip()
# #         line2 = line.rjust(len(line)).strip()        
#         test.append(line)
#         line2 = line2.strip().split()
#         test2.append(line2)
#         nitems.append(len(line2))
#     nitems = pd.Series(nitems).max()
#     nrows = len(test2)
#     maxwidth = pd.Series(widths).max
#     if hdr:
#         width = pd.Series(widths[1:]).max()
#         nitems = pd.Series(nitems[1:]).max()
#         test = [line[:width] for line in test[1:]]
#         colnames = test2[0][:nitems]
#         nrows = len(test2[1:])

