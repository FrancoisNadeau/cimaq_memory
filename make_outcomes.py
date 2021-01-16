import glob
import nibabel as nib
import nilearn
import numpy as np
import os
import pandas as pd
import random
import re
import scipy
import sys
import zipfile

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
from pandas import DataFrame as df
from cimaq_utils import flatten
from cimaq_utils import get_encoding
from cimaq_utils import loadimages

def make_outcomes():
    cimaq = loadinfos2()
    tmp = []
    for row in cimaq.iterrows():
        enc = pd.read_csv(row[1]['events'], sep='\t').drop('Unnamed: 0', axis=1)
        enc = enc.rename(columns={'stimOnsetSec':'onset',
                                  'Condition': 'trial_type'})
        ret = pd.read_csv(row[1]['behavioural'], sep='\t').drop('Unnamed: 0', axis=1)
        con = pd.read_csv(row[1]['confounds'], sep='\t')
        con = con.where(con.scrub == 1)
        scaninfos = scan_infos = dict(nib.load(row[1]['func']).header)
        ret['Spatial_RT'] = ret['Spatial_RT'].values/1000
        enc.trial_type.rename({})
        t_r = nib.load(row[1]['func']).header.get_zooms()[3]
        enc['duration'] = enc.onset.diff()
        enc['unscanned'] = (enc.onset + enc.duration) >= t_r * scan_infos['dim'][4]
        
     # Scoring
        memsheet = pd.merge(enc, ret, left_on='ImageID',
                            right_on='OldNumber').set_index('tNumXcond',
                                                            drop=False)
        toscrub = memsheet.where(memsheet.unscanned).dropna()
        memsheet = memsheet.drop(toscrub.index)
        memsheet['category'] = memsheet['category'].replace({'OLD': 1, 'New':2})
        memsheet['recogAcc'] = memsheet.category == memsheet.Recognition_RESP
        memsheet['CorrectSource'] = [int(val) for val
                                     in memsheet.CorrectSource.values]
        memsheet['Spatial_RESP'] = [int(float(val)) for val
                                    in memsheet.Spatial_RESP.replace({'False': False})]
        memsheet['spaceAcc'] = memsheet.CorrectSource \
                               == memsheet.Spatial_RESP
        memsheet['hit'] = [row[1]['recogAcc'] and row[1]['spaceAcc'] == True \
                           and row[1]['recogAcc'] == True
                           for row in memsheet.iterrows()]
        memsheet['rejOk'] = [row[1]['recogAcc'] and row[1]['spaceAcc'] == True \
                             and row[1]['category'] == 'OLD'
                             for row in memsheet.iterrows()]
        memsheet['recogOkSrcMiss'] = [row[1]['recogAcc'] == True \
                                 and row[1]['spaceAcc'] == False \
                                 and row[1]['category'] == 'OLD'
                                 for row in memsheet.iterrows()]
        memsheet['miss'] = [row[1]['recogAcc'] or row[1]['spaceAcc']== False
                            for row in memsheet.iterrows()]
        memsheet['recogMissSrcOk'] = [row[1]['recogAcc'] == False
                                      and row[1]['spaceAcc'] == True
                                      for row in memsheet.iterrows()]
        ctl = enc.loc[['CTL' in row[1].tNumXcond
                      for row in enc.iterrows()]]
        memsheet = memsheet[['recogAcc', 'hit', 'rejOk', 'recogOkSrcMiss',
                             'miss', 'recogMissSrcOk']]
        [os.makedirs(join(dname(dname(dname(row[1]['events']))), 'taskfiles2', 'events2'), exist_ok=True)]
        [os.makedirs(join(dname(dname(dname(row[1]['events']))), 'taskfiles2', 'ctlonly'), exist_ok=True)]
        [os.makedirs(join(dname(dname(dname(row[1]['events']))), 'taskfiles2', 'scores'), exist_ok=True)]
        enc.to_csv(join(dname(dname(dname(row[1]['events']))), 'taskfiles2', 'events2', row[0]+'events2.tsv'))
        ctl.to_csv(join(dname(dname(dname(row[1]['events']))), 'taskfiles2', 'ctlonly', row[0]+'ctlonly.tsv'))
        enc.to_csv(join(dname(dname(dname(row[1]['events']))), 'taskfiles2', 'scores', row[0]+'score.tsv'))

        tmp.append((enc, ctl, memsheet))
    return tmp

def main():
    make_outcomes()

if __name__ == '__main__':
    main()
