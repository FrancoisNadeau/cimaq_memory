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

def megamerge(dflist, merge_on, howto):
    return reduce(lambda x, y: pd.merge(x, y,
                                        on=merge_on,
                                        how=howto).astype('object'),
                  dflist)

def loadmeansheets():
    cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    failedQC = [str(ind) for ind in pd.read_csv(join(xpu(cimaq_dir),
                                'memoTask_ParticipantFile.tsv'),
                           sep='\t').dropna()[['dccid']].set_index('dccid').index]
    meansheets = df.from_dict(dict((bname(itm).split('_')[0],
                                    (itm, pd.read_csv(itm,
                                                      sep='\t', dtype='object').dropna()))
                                   for itm in sorted(loadimages(join(xpu(cimaq_dir),
                                                                     'meansheets')))),
                              orient='index', columns=['paths', 'sheets'])
    meansheets.sheets.meanMotion = meansheets.sheets.meanMotion.rename(
        columns={'total_scrubbed': 'total_scrubbed_frames'})
   # Check fMRI data availability per subject
    meansheets.sheets.bids['fMRI'] = meansheets.sheets.bids['fMRI'].replace(
        {'yes': True, not 'yes': False})
    meansheets.sheets.bids = meansheets.sheets.bids.where(
        meansheets.sheets.bids.fMRI == True)
    meansheets2 = megamerge([sheet.dropna() for sheet in meansheets.sheets],
                            merge_on = 'dccid', howto='inner')
    meansheets.sheets = [meansheets2[[col for col in sheet.columns
                                      if col in meansheets2.columns]].dropna().set_index('dccid')
                         for sheet in meansheets.sheets]
#     p1 = pd.read_csv(join(xpu(cimaq_dir), 'meansheets', 'taskpaths_participants.tsv'), sep='\t')
    return meansheets

def loadpaths(datadir='CIMAQ_fmri_memory_data_neuromod_DATA/data'):
    cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    cimaq_dir = xpu(cimaq_dir)
    test = pd.Series([bname(itm) for itm
                      in ls(join(xpu(cimaq_dir), datadir))]).unique()
    test2 = [itm for itm in loadimages(join(xpu(cimaq_dir), datadir))
             if 'sub' in itm]
    test3 = pd.Series([bname(itm).split('_')[1] for itm in test2]).unique()
    test4 = df([[[itm for itm in test2 if att and sub in itm][0]
                 for sub in test3] for att in test],
               index=test, columns=test3).T
    test4['dccid'] = [ind.split('sub')[1] for ind in test4.index]
    return test4.dropna()

def makeindexes():
    meansheets = loadmeansheets()
    datas = loadpaths()
    mtmpindx = [itm for itm in loadmeansheets().sheets.behav.astype('object').index
                if itm in datas.dccid.values]
    return mtmpindx

def loadinfos():
    meansheets = loadmeansheets()
#     datas = loadpaths()
#     mtmpindx = [itm for itm in loadmeansheets().sheets.behav.astype('object').index
#                 if itm in datas.dccid.values]
    datas = loadpaths()
    datas['subdccid'] = datas.index
    uindx = makeindexes()
    datas = datas.set_index('dccid', drop=False).loc[uindx]
    datas = datas.set_index('subdccid')
    subinfos = df(((subject, df(((row[0], row[1]['sheets'].loc[subject])
                     for row in meansheets.iterrows()),
                    columns=[subject, 'infos']).iloc[:3,].T) 
                     for subject in uindx),
                 columns=['dccid', 'infos'])

    return pd.merge(subinfos, datas, on='dccid').set_index('dccid')



