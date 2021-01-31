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

cimaq_dir = xpu('~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives')
zeprimes = join(cimaq_dir, 'task_files/zipped_eprime')
uzeprimes = join(dname(zeprimes), 'uzeprimes')

def get_infodf(indir):
    encdf = get_clean_encodings(indir)
    diadf = df([get_dialect(row[1]['fpath'], encod=row[1]['encod'])
                for row in encdf.iterrows()])
    return pd.merge(left=encdf, right=diadf, on='fname', how='outer')

def listat(inds, inpt):
    '''
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
    '''
    evlst, odlst = oddeven([itm[0] for itm in inpt])
    evvals = itemgetter(*[itm[0] for itm in
                          enumerate(inds)])(inpt)
    odvals = itemgetter(*[itm[0] for itm in
                          enumerate(inds)])(inpt)
    return evvals, odvals

def oddeven(inpt): 
    ''' 
    Source: https://www.geeksforgeeks.org/python-split-even-odd-elements-two-different-lists
    '''
    evelist = [ele[1] for ele in enumerate(inpt) if ele[0]%2 ==0] 
    oddlist = [ele[1] for ele in enumerate(inpt) if ele[0]%2 !=0]
    return evelist, oddlist    

def get_dialect(filename, encod):
    '''
    Source: https://wellsr.com/python/introduction-to-csv-dialects-with-the-python-csv-module/#DialectDetection
        - hdr variable replaces csv.Sniffer().has_header, which wouldn't work everytime
        Source: https://stackoverflow.com/questions/15670760/built-in-function-in-python-to-check-header-in-a-text-file
    Description: Prints out all relevant formatting parameters of a dialect
    '''
    with open(filename, encoding=encod) as src:
        dialect = csv.Sniffer().sniff(src.readline())
        hdr = src.read(1) not in '.-0123456789'
        if hdr:
            hdr = 0
        else:
            hdr = False
#         hdr = csv.Sniffer().has_header(src.readline())          
        nrows = len([line for line in src.readlines()])
        valuez = [bname(filename), hdr, dialect.delimiter,
                  nrows, dialect.doublequote, dialect.escapechar,
                  dialect.lineterminator, dialect.quotechar,
                  dialect.quoting, dialect.skipinitialspace]
        cnames =['fname', 'has_header', 'sep', 'n_rows',
                 'doublequote', 'escapechar',
                 'lineterminator', 'quotechar',
                 'quoting', 'skipinitialspace']
        dialect_df = pd.Series(valuez, index=cnames)
        src.close()
        return dialect_df
        
def megamerge(dflist, howto, onto=None):
    return reduce(lambda x, y: pd.merge(x, y,
                                        on=onto,
                                        how=howto).astype('object'),
                  dflist)

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

# ZipFile behaviour control
############################
def getnamelist(filename): 
    '''
    Adjustment to ZipFile.namelist() function to prevent MAC-exclusive
    '__MACOSX' and '.DS_Store' files from interfering.
    Only necessary for files compressed with OS 10.3 or earlier.
    Source: https://superuser.com/questions/104500/what-is-macosx-folder
    Command line solution:
        ``` zip -r dir.zip . -x ".*" -x "__MACOSX"
    Source: https://apple.stackexchange.com/questions/239578/compress-without-ds-store-and-macosx
    '''
    return [itm for itm in
            zipfile.ZipFile(filename).namelist()
            if  bname(itm).startswith('.') == False \
            and '__MACOSX' not in itm \
            and 'textClipping' not in itm]

# def getinfolist(filename):
#     namelist = getnamelist(filename)
#     temp = [zipfile.ZipFile(filename).getinfo(mmbr)
#                 for mmbr in namelist]
#     comlist = []
#     for itm in temp:
#         if itm.comment:
#             comlist.append((itm.filename, itm.comment))
#             itm.comment = ''
#     comlistpath = xpu(join('~/',bname(itm.filename)+'.tsv'), sep='\t')
#     comlist = df(comlist).to_csv(
        
#     return temp

def getinfolist(filename):
    namelist = getnamelist(filename)
    return [zipfile.ZipFile(filename).getinfo(mmbr)
                for mmbr in namelist]
    
def cleanarchv(indir, outdir):
    os.makedirs(join(dname(indir), outdir), exist_ok=True)
    [shutil.move(itm, join(outdir, bname(itm)))
     for itm in loadimages(indir)
     if os.path.isfile(itm) and not itm.endswith('.zip')]

def uzipfiles(indir, outdir):
    outdir = join(dname(indir), outdir)
    for item in tqdm([itm for itm in loadimages(indir)
                      if not itm.startswith('.')]):
        with zipfile.ZipFile(item, 'r') as archv:
            archv.extractall(path=join(outdir,
                                       splitext(bname(item))[0]),
                             members=getinfolist(item))
        archv.close()
    cleanarchv(indir, outdir)
    [shutil.move(
        itm,join(outdir, bname(itm).lower().replace(' ', '_').replace('-', '_')))
     for itm in
             loadimages(outdir)]
    removeEmptyFolders(indir)
    removeEmptyFolders(outdir)

####################################    

# def uzipfiles(indir, outdir):
#     outdir = join(dname(indir), outdir)
#     for item in tqdm([itm for itm in loadimages(indir)
#                       if not itm.startswith('.')]):
#         with zipfile.ZipFile(item, 'r') as archv:
#             archv.extractall(path=join(outdir,
#                                        splitext(bname(item))[0]),
#                              members=getinfolist(item))
#         archv.close()
#     cleanarchv(indir, outdir)
#     [shutil.move(
#         itm,join(outdir, bname(itm).lower().replace(' ', '_').replace('-', '_')))
#      for itm in
#              loadimages(outdir)]
#     removeEmptyFolders(indir)
#     removeEmptyFolders(outdir)
################################

# Get file encodings and sort accordingly    
def get_all_encodings(indir):  
    allfiles = [itm for itm in
                loadimages(indir)
                if not itm.startswith('.')]
    return df(tuple(zip([bname(itm) for itm in allfiles],
                        allfiles, [get_encoding(fname)
                                   for fname in allfiles])),
              columns=['fname', 'fpath', 'encod'])

def no_encod(encdf):
    nodet = encdf.loc[[row[1]['encod'] == None
                      for row in encdf.iterrows()]]
    return flatten([[itm for itm in list(encdf.fpath)
                     if splitext(fname)[0] in itm]
                    for fname in nodet.fname])

def clearnoencod(encdf):
#     encdf = get_all_encodings(indir=uzeprimes)
    noenc = no_encod(encdf)
    [os.remove(fpath) for fpath in noenc]

def get_clean_encodings(indir=uzeprimes):
    encdf = get_all_encodings(indir)
    clearnoencod(encdf)
    encdf = get_all_encodings(indir)
    extlst = encdf.insert(loc=1, column='ext',
                          value=[splitext(fname)[1]
                                 for fname in encdf.fname])
    return encdf                    

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

def prepsheet(filename, encod=None):
    if encod:
        encod = get_encoding(filename)
    else: encod = encod
    sheet = open(filename , "r", encoding=encod)
    test = [no_ascii(line.rstrip().replace('\t', '    ')).split()
            for line in sheet.readlines()]
    ncols = np.array([len(itm) for itm in test]).max()
    values = [line[:ncols] for line in test]        
    colnames = None    
    hdr = bool(sheet.read(1) in '.-0123456789')
    if hdr:
        ncols = np.array([len(itm) for itm in test[1:]]).max()
        values = [line[:ncols-1] for line in test[1:]]
        colnames = test[0][:ncols-1]
    test = df(pd.read_json(json.dumps(values)).values,
              columns=colnames)
    test = test.sort_index()
    test.columns = map(str.lower, test.columns)
    test.columns = map(str.strip, test.columns)
    if test.shape[1] > 2:
        test = test.dropna(axis=1, how='all')
    else:
        test = test
    sheet.close()
    return test

def flattendict(d, parent_key='', sep='_'):
    '''
    Source:
    https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
    '''
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

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
    results: Pandas 'Series' (index=["encoding", "confidence"], name="sheetname")
    "language" is dropped because it is known a priori to be Python
    '''
    detector = udet()
    bsheet = open(sheetpath , "rb")
    for line in bsheet.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    return detector.result['encoding']

def get_encoding2(sheetlist):
    ''' 
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

def get_encodingfull(sheetpath):
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
    results: Pandas 'Series' (index=["encoding", "confidence"], name="sheetname")
    "language" is dropped because it is known a priori to be Python
    '''
    detector = udet()
    bsheet = open(sheetpath , "rb")
    for line in bsheet.readlines(line.getvalues):
        detector.feed(line)
        if detector.done: break
    detector.close()
    bsheet.close()
    return detector.result

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

def file2gzip(filename):
    with open(filename, 'rb') as tozip:
        with gzip.open(join(dname(filename),
                            bname(filename)+'.gz'), 'wb') as zfile:
            shutil.copyfileobj(tozip, zfile)
    zfile.close()
    tozip.close()

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

def loadsheets(snames, indir=join(cimaq_dir, 'participants')):
    sheetnames = [join(indir, name)
                  for name in snames]
    sheetnames = df(((splitext(bname(sheet))[0],
                      splitext(bname(sheet))[1],
                      sheet) for sheet
                       in sheetnames),
                    columns=['sheetnames', 'ext', 'sheetpaths'])
    sheetnames['sheetvalues'] = [prepsheet(spath).dropna(axis=0)
                                 for spath in sheetnames.sheetpaths]  
    return sheetnames            
            
# To be tested            
# # change your naming to fit with common naming standards for
# # variables and functions, pep linked below
# def get_duplicate_columns(df):
#     '''
#     You are looking for non-repeated combinations of columns, so use
#     itertools.combinations to accomplish this, it's more efficient and
#     easier to see what you are trying to do, rather than tracking an index
#     '''
#     duplicate_column_names = set()
#     # Iterate over all pairs of columns in df
#     for a, b in itertools.combinations(df.columns, 2):
#         # will check if every entry in the series is True
#         if (df[a] == df[b]).all():
#             duplicate_column_names.add(b)

#     return list(duplicate_column_names)

###############################################################################  
###################################
##### CIMA-Q SPECIDICS ############



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
    
