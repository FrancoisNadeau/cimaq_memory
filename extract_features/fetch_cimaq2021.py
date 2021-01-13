#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import glob
# import nibabel as nib
# import nilearn
import numpy as np
import os
import pandas as pd
import random
import re
import scipy
# import sys
# import zipfile

from functools import reduce
# from matplotlib import pyplot as plt
# from nilearn.plotting import plot_design_matrix
# from nilearn.glm.first_level import FirstLevelModel
# from nilearn.glm.first_level import make_first_level_design_matrix
# from nilearn import image
# from nilearn import plotting
# from nilearn.plotting import plot_stat_map, plot_anat, plot_img, show
# from numpy import nan as NaN

from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df
from cimaq_utils import flatten
from cimaq_utils import loadimages
# from get_new_events import get_new_events

def loadmeansheets(ndir):
    subbids = pd.read_csv(join(os.getcwd(), 'participants_cimaq_03-19.tsv'),
                          sep='\t').rename(columns={'participant_id': 'dccid'})
    subbids = subbids.rename(columns=str.lower)
    behav = pd.read_csv(
                join(os.getcwd(), 'fMRI_behavMemoScores.tsv'),
                sep='\t').sort_index().rename(columns=str.lower)
    behav['dccid'] = subbids['dccid']

    encoding = pd.read_csv(join(os.getcwd(), 
                                'memoTaskParticipantFile_cimaq_03-19.tsv'),
                           sep='\t').sort_index().rename(columns= \
                               {'participant_id': 'dccid'})
    encoding = encoding.rename(columns=str.lower)

    npsych = pd.read_csv(join(
             os.getcwd(),'ALL_Neuropsych_scores.tsv'),
                     sep='\t').sort_index().rename(\
                         columns={'id': 'dccid'}).rename(columns=str.lower)

    meanmotion = pd.read_csv(
                     join(os.getcwd(), 'fMRI_meanMotion.tsv'),
                     sep='\t').rename(\
                         columns={'id': 'dccid'}).rename(\
                             columns=str.lower).sort_index()

    # Check fMRI data availability per subject
    subbids['fmri'] = subbids['fmri'].replace({'yes': True,
                                               not 'yes': False})
    subbids = subbids.rename({'participant_id':'dccid'}, axis=1)
    subbids = subbids.where(subbids.fmri == True)

    # Check quality control passation status
    failed = encoding.loc[(encoding.qc_status == 'F')]
    encoding = encoding.drop(failed.index)
    failed.to_csv(join(os.getcwd(), 'failed_qc.tsv'))

    # Check neuropsychological testing, motion confonds
    # and retrieval task performance data availability
    npsych = npsych.dropna()
    meanmotion = meanmotion.dropna()
    behav = behav.dropna()

    # subbids, encoding, npsych, meanmotion, behav
    finalsort_a = pd.merge(subbids.dropna(), encoding, on='dccid')
    finalsort_b = pd.merge(finalsort_a, npsych, on='dccid')
    finalsort_c = pd.merge(finalsort_b, meanmotion, on='dccid')
    finalsort_d = pd.merge(finalsort_c,
                           behav, on='dccid')
    attendances = [int(dccid) for dccid
                   in finalsort_d['dccid'].dropna().values.tolist()]
    subbids = subbids.set_index('dccid').loc[attendances]
    encoding = encoding.set_index('dccid').loc[attendances]
    encoding['sub-dccid'] = ['sub-' + str(ind)
                             for ind in encoding.index]
    encoding = encoding.set_index('sub-dccid')
    npsych = npsych.set_index('dccid').loc[attendances]
    npsych['sub-dccid'] = ['sub-' + str(ind)
                           for ind in npsych.index]
    npsych.set_index('sub-dccid')
    meanmotion = meanmotion.set_index('dccid').loc[attendances]
    meanmotion['sub-dccid'] = ['sub-' + str(ind)
                               for ind in meanmotion.index]
    meanmotion.set_index('sub-dccid')
    behav = behav.set_index('dccid').loc[attendances]
    behav['sub-dccid'] = ['sub-' + str(ind)
                          for ind in behav.index]
    behav = behav.set_index('sub-dccid')
    subbids = subbids.drop('fmri', axis=1).dropna()
    subbids['sub-pscid'] = ['sub-' + str(ind)
                            for ind in subbids.pscid]
    encoding = encoding.drop('qc_status', axis=1)
    os.makedirs(ndir, exist_ok=True)
    subbids.to_csv(join(ndir, 'subjects_bids.tsv'), sep='\t')
    return subbids, encoding, npsych, meanmotion, behav

def fetch_cimaq2021(ndir='fetched_cimaq'):
    ndir = join(os.getcwd(), ndir)
    taskdir=xpu("~/cimaq_events2020")
    datadir = '/media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA/CIMAQ_fmri_memory_data_neuromod_DATA/data'
    subbids, encoding, npsych, meanmotion, behav = loadmeansheets(ndir)
    subbids = pd.read_csv(join(os.getcwd(), 'newsheets2',
                               'subjects_bids.tsv'), sep='\t')
    start = [sheet for sheet in loadimages(taskdir)
                                if sheet.endswith('.tsv') \
                                and 'Motionfile' in sheet]
    p1 = df(tuple(zip([bname(dname(sheet))
                       for sheet in start],
                      start)), columns=['sub-pscid',
                                        'subpaths'])
    p1['motion'] = start
    p1 = pd.merge(p1, subbids, on='sub-pscid')
    p1['anat'] = [[img for img in loadimages(join(datadir, 'anat'))
                  if str(dccid) in bname(img)][0]
                  for dccid in p1.dccid]
    p1['func'] = [[img for img in loadimages(join(datadir, 'fmri_resample'))
                  if str(dccid) in bname(img)][0]
                  for dccid in p1.dccid]
    p1['confounds'] = [[img for img in loadimages(join(datadir, 'confounds_resample'))
                  if str(dccid) in bname(img)][0]
                  for dccid in p1.dccid]
    p1['masks'] = [[img for img in loadimages(join(datadir, 'masks'))
                  if str(dccid) in bname(img)][0]
                  for dccid in p1.dccid]
    p1['sub-dccid'] = ['sub-' + str(dccid)
                       for dccid in p1.dccid]
    p1 = p1.set_index('sub-pscid').sort_index()
    p1['events'] = flatten([[join(taskdir, row[0], sheet)
                             for sheet in ls(join(taskdir, row[0]))
                                      if sheet.endswith('.tsv') \
                                      and 'Memory' in sheet]
                                     for row in p1.iterrows()])
    p1['retrieval'] = flatten([[sheet for sheet
                                in loadimages(join(taskdir, row[0]))
                                if sheet.endswith('.tsv') \
                                and 'Retrieval' in sheet]
                                for row in p1.iterrows()])

    subbids = subbids.set_index('sub-pscid')
    subbids = subbids.loc[p1.index]
    p1 = p1.drop(subbids.columns, axis=1)
    newdatadir = './fetched_datas'
    p1.to_csv(join(newdatadir, 'p1.tsv'), sep='\t')
    subbids.to_csv(join(newdatadir, 'subbids.tsv'), sep='\t')
    p1 = p1.set_index('sub-dccid')
    subbids['sub-dccid'] = ['sub-' + str(row[1]['dccid'])
                            for row in subbids.iterrows()]
    subbids = subbids.set_index('sub-dccid').sort_index()
    meanmotion = meanmotion.set_index('sub-dccid').loc[subbids.index].sort_index()
    npsych = npsych.set_index('sub-dccid').loc[subbids.index].sort_index()
    encoding = encoding.loc[subbids.index].sort_index()
    behav = behav.loc[subbids.index].sort_index()
    subbids.to_csv(join(ndir, 'subjects_bids.tsv'), sep='\t')
    encoding.to_csv(join(ndir, 'subjects_memorytask.tsv'), sep='\t')
    npsych.to_csv(join(ndir, 'subjects_npsychresults.tsv'), sep='\t')
    meanmotion.to_csv(join(ndir, 'subjects_meanmotion.tsv'), sep='\t')
    behav.to_csv(join(ndir, 'subjects_retrieval.tsv'), sep='\t')

    return p1, subbids, encoding, npsych, meanmotion, behav
    
# def main():
#     p1, subbids, encoding, npsych, meanmotion, behav = fetch_cimaq2021()
#     return p1, subbids, encoding, npsych, meanmotion, behav

# if __name__ == "__main__":
#     main()

