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
from cimaq_utils import loadimages

from extract_all_events import extract_all_events
from clean_all_events import clean_all_events

def loadpaths(datadir='CIMAQ_fmri_memory_data_neuromod_DATA/data'):
    cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
    cimaq_dir = xpu(cimaq_dir)
    test = pd.Series([bname(itm) for itm
                      in ls(join(xpu(cimaq_dir), datadir))]).unique()
    test2 = loadimages(join(xpu(cimaq_dir), datadir))
    test3 = pd.Series([bname(itm).split('_')[1] for itm in test2]).unique()
    test4 = df([[[itm for itm in test2 if att and sub in itm][0]
                 for sub in test3] for att in test],
               index=test, columns=test3).T
    test4['dccid'] = [ind.split('sub')[1] for ind in test4.index]
    return test4.dropna()

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

def loadinfos(subject):
    meansheets = loadmeansheets()
    subsheets = loadpaths()
    subsheets = subsheets.set_index('dccid', drop=False).loc[subject]
    subinfos = df(((row[0], row[1]['sheets'].loc[subject])
                   for row in subsheets.iterrows()),
                  columns=[subject, 'infos']).iloc[:3,].set_index(subject)
    test = pd.merge(subinfos, subsheets, on='dccid')
    return test

def common_indx():
    meansheets, subsheets = loadmeansheets(), loadpaths()
    meansheets.sheets
    subsheets = subsheets.set_index('dccid', drop=False)

#     subinfos = dict(tuple(zip(['paths', 'bids', 'memory_factors',
#                                'mean_confounds', 'confusion_matrix'],
#                               [sheet.loc[subject] for sheet in subsheets.sheets])))
    
class cimaq_ds():
    def __init__():
        class participant():
            def __init__(self):
                self.name, self.subinfos, self.datas = loadinfos()
        def  __init__():
            self.taskdata = loadpaths()
            self.meansheets = loadmeansheets()
            self.participants = dict(())

            
        
def make_cimaq():
    extract_all_events()
    clean_all_events()
    meansheets = loadmeansheets()
    tasksheets = loadpaths()


#    subject = meansheets.sheets.taskpaths['subdccid'].sample().index.values[0]



