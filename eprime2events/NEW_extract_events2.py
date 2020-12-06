#!/usr/bin/env python
# encoding: utf-8

import csv
import ctypes
import json
import os
import re
import sys
import numpy as np
import pandas as pd
import shutil
import time
import zipfile
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df
from cimaq_utils import flatten
from cimaq_utils import loadimages

def NEW_extract_events2(
    zipdir="~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/zipped_eprime",
    outdir="~/cimaq_extracted_eprime0"):
    '''
    Description
    -----------
    - Extracts zipped E-prime files to directories with BIDS compliant structure.
    - Sorts participants task files from other data
        - eg. medical, consent, anamnesis and other pencil-paper forms
    - Ensures lossfree and complete extraction with 'zipfile context mamnager'
    - Saves useful '.tsv' sheet for the following steps
        - Similar to BIDS mandatory 'participants.tsv' file
    
        Source & Docs: https://docs.python.org/3/library/zipfile.html
        Ressources & Tutos: https://pymotw.com/2/zipfile/
        
    Parameters
    ----------
    - zipdir: string or 'os.path' compatible object pointing to zipped eprime files directory
    - outdir: string or 'os.path' compatible object pointing to desired extraction directory
    
    Returns
    -------
    None
    '''
    
    # Initializing BIDS compliant participants sheet
    outdir, zipdir = xpu(outdir), xpu(zipdir)
    participants = df([("sub-"+bname(zfile).split("_")[0],
                        bname(zfile).split("_")[0],
                        bname(zfile).split("_")[1],
                        bname(zfile),
                        zfile,
                        join(outdir, "sub-"+bname(zfile).split("_")[0], "archive"))
                       for zfile in loadimages(zipdir) if zfile.endswith(".zip")],
                      columns=["sub-ID", "pscid","dccid", "zfilename",
                               "zipdirpaths", "extdirpaths"]).set_index("sub-ID").sort_index()
    
    # Generate all destination folders at once
    # - except top directory (must exist)
    [os.makedirs(extdirpath, exist_ok=True)
     for extdirpath in participants.extdirpaths]
    for row in participants.iterrows():
        with zipfile.ZipFile(row[1]["zipdirpaths"], "r") as archv:
            row[1]["archnames"] = archv.namelist()
            archv.extractall(row[1]["extdirpaths"])
            archv.close()

    participants["nitems_pre"] = [len(ls(join(outdir, row[0])))
                              for row in participants.iterrows()]

    # Move good files to new BIDS folder
    [[shutil.move(item, join(outdir, row[0], bname(item)))
      for item in loadimages(row[1]["extdirpaths"])
      if not item.endswith(".edat2") and not "PRATIQUE" in item
        and not os.path.isdir(join(outdir, row[0], item)) and item.endswith(".txt")]
     for row in participants.iterrows()]

    participants["nitems_post"] = [len(ls(join(outdir, row[0]))) for row in participants.iterrows()]
    participants.to_csv(join(outdir, "participants.tsv"), sep='\t')

def main():
    NEW_extract_events2()

if __name__ == '__main__':
    main()
