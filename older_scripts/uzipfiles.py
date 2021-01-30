#!/usr/bin/env python

import os
import shutil
import zipfile
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from os.path import splitext

from cimaq_utils import loadimages

def getnamelists(filename, delim='__MACOSX'):           
    return [itm for itm in
            zipfile.ZipFile(filename).namelist()[:1]
            if delim not in itm]

def uzipfiles(indir='~/../../media/francois/seagate_1tb/CIMAQ_fmri_memory/data/task_files/zipped_eprime'):
    indir = xpu(indir)
    items = [(item, getnamelists(item))
              for item in loadimages(indir)]
    for item in items:
        for mmbr in item[1]:
            with zipfile.ZipFile(item[0]) as archv:
                archv.extract(member=mmbf)
            archv.close()
#     os.makedirs(join(dname(indir), outdir), exist_ok=True)
#     [shutil.move(itm, join(dname(indir), outdir, bname(itm)))
#      for itm in loadimages(indir) if not itm.endswith('.zip')]
        
def main():
    uzipfiles()

if __name__ == '__main__':
    main()