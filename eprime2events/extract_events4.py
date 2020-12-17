#!/usr/bin/env python

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
from tqdm import tqdm
from cimaq_utils import flatten
from cimaq_utils import loadimages

def extract_events4(
    zipdir="~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/zipped_eprime",
    outdir="~/extracted_eprime2020"):

    # Initializing BIDS compliant participants sheet
    outdir, zipdir = xpu(outdir), xpu(zipdir)
    participants = df([("sub-"+bname(zfile).split("_")[0],
                        bname(zfile).split("_")[0],
                        bname(zfile).split("_")[1],
                        bname(zfile),
                        zfile,
                        join(outdir,
                             "sub-"+bname(zfile).split("_")[0],
                             "archive"))
                       for zfile in loadimages(zipdir)
                       if zfile.endswith(".zip")],
                      columns=["sub-ID", "pscid","dccid", "zfilename",
                               "zipdirpaths",
                               "extdirpaths"]).set_index("sub-ID").sort_index()

    [os.makedirs(extdirpath, exist_ok=True)
     for extdirpath in participants.extdirpaths]
    
    for row in tqdm(participants.iterrows()):
        with zipfile.ZipFile(row[1]["zipdirpaths"], "r") as archv:
            archv.extractall(row[1]["extdirpaths"],
                             members=[item for item in archv.namelist()
                                      if not item.split("/")[1].startswith("._")])
        archv.close()
                                
    # Move good files to new BIDS folder
    [[shutil.move(item, join(outdir, row[0], bname(item)))
      for item in loadimages(row[1]["extdirpaths"])
      if not item.endswith(".edat2") \
          and "PRATIQUE" not in item
          and not os.path.isdir(join(outdir, row[0], item)) \
          and not item.startswith("._")
          and "CIMAQ" in item]
     for row in participants.iterrows()]
    # Save participants sheet to tsv
    participants.to_csv(join(outdir, "participants.tsv"), sep='\t')

def main():
    extract_events4()

if __name__ == '__main__':
    main()
