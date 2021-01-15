#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

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

def NEW_extract_events3_iso8859(
    zipdir="~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/zipped_eprime",
    outdir="~/extracted_eprime0_iso8859"):

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
    [os.makedirs(extdirpath, exist_ok=True) for extdirpath in participants.extdirpaths]
    for row in participants.iterrows():
        with zipfile.ZipFile(row[1]["zipdirpaths"], "r") as archv:
            row[1]["archnames"] = archv.namelist()
            archv.extractall(row[1]["extdirpaths"])
            archv.close()

    participants["nitems"] = [len(ls(join(outdir, row[0]))) for row in participants.iterrows()]

    # Move good files to new BIDS folder
    [[shutil.move(item, join(outdir, row[0], bname(item)))
      for item in loadimages(row[1]["extdirpaths"]) if not item.endswith(".edat2") and not "PRATIQUE" in item
	and not os.path.isdir(join(outdir, row[0], item)) and item.endswith(".txt")]
     for row in participants.iterrows()]

    participants.to_csv(join(outdir, "participants.tsv"), sep='\t')

def main():
    NEW_extract_events3_iso8859()

if __name__ == '__main__':
    main()
