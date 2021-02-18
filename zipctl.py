#!/usr/bin/env python3

import gzip
import lzma
import os
import shutil
import tarfile
import zipfile

from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join as pjoin
from tqdm import tqdm
from removeEmptyFolders import removeEmptyFolders
from cimaq_utils import loadimages

########### ZipFile Behaviour Control Toolbox #################################

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
    return tuple(sorted(list(itm for itm in
                             zipfile.ZipFile(filename).namelist()
                             if  bname(itm).startswith('.') == False \
                             and '__MACOSX' not in itm \
                             and 'textClipping' not in itm
                             and itm != os.path.splitext(bname(dname(itm)))[0]+'/')))

def getinfolist(filename):
    namelist = getnamelist(filename)
    return tuple(zipfile.ZipFile(filename).getinfo(mmbr)
                 for mmbr in namelist)
    
def cleanarchv(indir, outdir):
    os.makedirs(pjoin(dname(indir), outdir), exist_ok=True)
    [shutil.move(itm, pjoin(outdir, bname(itm)))
     for itm in loadimages(indir)
     if os.path.isfile(itm) and not itm.endswith('.zip')]

def uzipfiles(indir, outdir=None):
    if outdir != None:
        outdir = outdir
    else:
        outdir = pjoin(dname(indir), 'uz_'+bname(indir))
    os.makedirs(outdir, exist_ok=True)
    for item in tqdm([itm for itm in loadimages(indir)
                      if not itm.startswith('.')]):
        with zipfile.ZipFile(item, 'r') as archv:
            archv.extractall(path=pjoin(outdir,
                                       os.path.splitext(bname(item))[0]),
                             members=getnamelist(item))
        archv.close()
    [shutil.move(
        itm,pjoin(outdir,
                  bname(itm).lower().replace(' ', '_').replace('-', '_')))
     for itm in loadimages(outdir)]
    removeEmptyFolders(indir)
    removeEmptyFolders(outdir)
    
def file2gzip(filename):
    with open(filename, 'rb') as tozip:
        with gzip.open(pjoin(dname(filename),
                            bname(filename)+'.gz'), 'wb') as zfile:
            shutil.copyfileobj(tozip, zfile)
    zfile.close()
    tozip.close()
