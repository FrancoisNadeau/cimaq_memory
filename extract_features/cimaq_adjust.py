#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nibabel as nib
import os
import pandas as pd
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df
from cimaq_utils import flatten
from cimaq_utils import loadimages

def cimaq_adjust():
    p1 = pd.read_csv('./fetched_cimaq/p1.tsv', sep='\t')
    for row in p1.iterrows():
        encsheet = pd.read_csv(row[1]['events'],
                                      sep='\t').drop('Unnamed: 0', axis=1)
        encsheet['trial_num'] = encsheet.index
        retsheet = pd.read_csv(row[1]['retrieval'],
                               sep='\t').drop('Unnamed: 0', axis=1)
        retsheet['Spatial_RT'] = retsheet['Spatial_RT'].values/1000
        encsheet['trialDur'] = encsheet['fixDurSec'] + encsheet['stimDurSec']
        encsheet['isi'] = encsheet['stimOnsetSec'].diff()
        encsheet['isiFix'] = encsheet['fixOnsetSec'].diff()
        encsheet['trial_end'] = encsheet.trialDur + encsheet.stimOnsetSec
        encsheet['unscanned'] = encsheet.trial_end >= nib.load(row[1]['func']).header.get_zooms()[3] * \
                                dict(nib.load(row[1]['func']).header)['dim'][4]
                                
        encsheet.to_csv(row[1]['events'], sep='\t')
        retsheet.to_csv(row[1]['retrieval'], sep='\t')

def main():
    cimaq_adjust()

if __name__ == "__main__":
    main()
