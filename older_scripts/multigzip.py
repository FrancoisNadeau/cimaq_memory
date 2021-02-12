#!/usr/bin/env python

import gzip
import shutil
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from os.path import splitext
from tqdm import tqdm

from cimaq_utils import loadimages
from cimaq_utils import file2gzip

def multigzip(indir='', outdir=None):
    allfiles = loadimages(indir)
    for fname in tqdm(allfiles):
        file2gzip(fname)

def main():
    multigzip()

if __name__ == '__main__':
    main()
