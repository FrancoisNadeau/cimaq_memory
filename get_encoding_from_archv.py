#!/usr/bin/env python

import chardet
import scv
import os
import pandas

import glob
from chardet.universaldetector import UniversalDetectorljust 
from os.path import splitext
import gzip
import lzma
import zipfile
import tar
import csv
import glob
import io
import json
import magic
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
from io import StringIO
import sys
import tarfile
import xml.parsers.expat as xmlprse
import zipfile

from collections import Counter
from collections import OrderedDict
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
from os.path import splitext
from pandas import DataFrame as df
from tabulate import tabulate

from cimaq_utils import flatten
from cimaq_utils import get_encoding
from cimaq_utils import get_encoding2
from cimaq_utils import loadimages

from loading_utils import megamerge
from loading_utils import loadmeansheets
from loading_utils import loadpaths
from loading_utils import makeindexes
from loading_utils import loadinfos2
##########
# https://stackoverflow.com/questions/42079724/how-to-unpack-xz-file-with-python-which-contains-only-data-but-no-filename#comment76827284_42079784
# binary_data_buffer = lzma.open('test.txt.xz').read() , then string_buffer = binary_data_buffer.decode('utf-8')

# try:
#     import lzma
# except ImportError:
#     from backports import lzma

# print lzma.open('file.xz').read()

####################
# https://stackoverflow.com/questions/48434732/read-tar-gz-file-into-binary-string-python
# with open(filename,"rb") as f:
#     data = f.read()
#     import base64
# data = base64.b64encode(data)
########

# detector = udet()
# for filename in glob.glob('*.xml'):
#     print filename.ljust(60),
#     detector.reset()
#     for line in file(filename, 'rb'):
#         detector.feed(line)
#         if detector.done: break
#     detector.close()
#     print detector.result    
    
# def main():
#     get_encoding(filename)

# if __name__ == '__main__':
#     main()
    
    


zipcimaq = xpu('~/../../media/francois/seagate_8tb/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/zipped_eprime.zip')
def getlvl1(filename):
    archv = zipfile.ZipFile.open(filename, 'r')
    names = list(name for name in archv.namelist())
    cleannames = list(name.encode("ascii", "ignore") for name in names)
    
        decode_string = encoded_string.decode()
    archv.close()
    return infolst
getlvl1(zipcimaq)    
    
from chardet.universaldetector import UniversalDetector as udet

def get_encoding_from_archv(archvpath):
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
    
    extension = splitext(filename)

    

    detector = udet()
        archv = zipfile.ZipFile.open(filename, 'rb')
    infolst = archv.infolist()
    archv = zipfile.Path(archvpath).read_bytes()
    bsheet = open(sheetpath , "rb")
    for line in bsheet.readlines(line.getvalue()):
        detector.feed(line)
        if detector.done: break
    detector.close()
    archv.colse()
    detector.result    

    
    
