#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df

def loadmeansheets(ndir):
    '''
    Description
    -----------
    
    Loads all averaged participants data
     - Sociodemographic information (subbids)
     - Retrieval task performance (behav)
         - Unscanned
         - Goal is to predict THIS from the other data
     - Neuropsychological testing (npsych)
     - Motion confonds (meanmotion)
     - Encoding task performance (encoding)
     
    All sheets are indexed by participant identifier.
    However, CIMA-Q participants have 2 identifiers:
     - dccid (6-digit) & pscid (7-digit)
     
    Furthermore, not all participants underwent all tasks or tests.
    Sorting is achieved by:
        - Loading 'subbids'
            - Only sheet with both identifiers (base sheet)
        - Removing outliers and failed QC assertion
            - Made by Marie St-Laurent (2019)
            - Goal step of this function
        - Keep only participants for whom:
            - QC assertion is passed
            - Mean data is computed
        - Merging all sheets on a common participant identifier column
        - Splitting all sheets back with their original column names
        - Saving the sheets to csv
        
    Parameters
    ----------
    
        - ndir: default = './fetched_cimaq2021
                str or os.path-like object 
                Path to directory where sheets should be saved
    
    Returns
    -------
        - subbids, encoding, npsych, meanmotion, behav (see desxription)
            - Indexed, filtered and sorted
    '''
               
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
    npsych = npsych.set_index('dccid').loc[attendances]
    npsych['sub-dccid'] = ['sub-' + str(ind)
                           for ind in npsych.index]
    meanmotion = meanmotion.set_index('dccid').loc[attendances]
    meanmotion['sub-dccid'] = ['sub-' + str(ind)
                               for ind in meanmotion.index]
    behav = behav.set_index('dccid').loc[attendances]
    behav['sub-dccid'] = ['sub-' + str(ind)
                          for ind in behav.index]
    subbids = subbids.drop('fmri', axis=1).dropna()
    subbids['sub-pscid'] = ['sub-' + str(ind)
                            for ind in subbids.pscid]
    encoding = encoding.drop('qc_status', axis=1)
    encoding = encoding.set_index('sub-dccid')
    npsych.set_index('sub-dccid')
    meanmotion.set_index('sub-dccid')
    behav = behav.set_index('sub-dccid')
    return subbids, encoding, npsych, meanmotion, behav
