#!/usr/bin/env python

import csv
import os
import numpy as np
import pandas as pd
import shutil
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

######## ######## ######## ######## ######## ######## ######## ######## #######
# "~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/zipped_eprime"
def extract_all_events(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
    # Initializing BIDS compliant participants sheet
    zipdir='cimaq_03-19_derivatives_CIMAQ_fmri_memory_scripts/data/task_files/zipped_eprime'
    outdir = join(xpu(cimaq_dir), "extracted_eprimes2021")
    zipdir = join(xpu(cimaq_dir), zipdir)
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
                      columns=["sub-pscid", "pscid","dccid", "zfilename",
                               "zipdirpaths",
                               "extpaths"]).set_index("sub-pscid").sort_index()

    [os.makedirs(extdirpath, exist_ok=True)
     for extdirpath in participants.extpaths]
    
    for row in tqdm(participants.iterrows()):
        with zipfile.ZipFile(row[1]["zipdirpaths"], "r") as archv:
            archv.extractall(row[1]["extpaths"],
                             members=[itm for itm in archv.namelist()
                                      if not itm.split("/")[1].startswith("._")])
        archv.close()
                                
    # Move good files to new BIDS folder
    [[shutil.move(item, join(outdir, row[0], bname(item)))
      for item in loadimages(row[1]["extpaths"])
      if not item.endswith(".edat2") \
          and "PRATIQUE" not in item
          and not os.path.isdir(join(outdir, row[0], item)) \
          and not bname(item).startswith("._")
          and "CIMAQ" in item]
     for row in participants.iterrows()]
    
#     [[shutil.move(item, join(outdir, row[0], bname(item)))
#       for item in loadimages(row[1]["extpaths"])
#       if not item.endswith(".edat2") \
#           and "PRATIQUE" not in item
#           and not os.path.isdir(join(outdir, row[0], item)) \
#           and not item.startswith("._")
#           and "CIMAQ" in item]
#      for row in participants.iterrows()]
    # Save participants sheet to tsv
    participants.to_csv(join(xpu(cimaq_dir), "participants.tsv"), sep='\t')
    archvmvr = tuple(zip(participants.extpaths, [join(cimaq_dir, 'participants_archives',
                                                     bname(dname(extpath)) + bname(extpath))
                                                for extpath in participants.extpaths]))
    os.makedirs(dname(archvmvr[0][1]), exist_ok=True)
    [shutil.move(itm[0], itm[1]) for itm in archvmvr]

def main():
    extract_all_events()

if __name__ == '__main__':
    main()
