#!/usr/bin/env python

import os
import sys
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

def multi_zinfos(zipfolders):
    zinfos = []
    for zfd in tqdm(zipfolders):
        with zipfile.ZipFile(xpu(zfd), "r") as archv:
            zinfos.append(dict(info[1] for info in enumerate(archv.infolist())))
    return df(zinfos)

def main():
    multi_zinfos()
if '__name__' == '__main__':
    main()