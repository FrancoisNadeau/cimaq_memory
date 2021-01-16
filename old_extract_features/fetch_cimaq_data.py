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
from cimaq_utils import flatten
from cimaq_utils import loadimages
from loadmeansheets import loadmeansheets

def fetch_cimaq_data(ndir='fetched_cimaq'):
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
    p1['sub-pscid'] = ['sub-' + str(row[1]['pscid'])
                       for row in subbids.iterrows()] 
    subbids = subbids.set_index('sub-dccid').sort_index()
    meanmotion = meanmotion.set_index('sub-dccid').loc[subbids.index].sort_index()
    npsych = npsych.set_index('sub-dccid').loc[subbids.index].sort_index()
    encoding = encoding.loc[subbids.index].sort_index()
    behav = behav.loc[subbids.index].sort_index()
    
    try:
        os.path.isdir(ndir)
        pass
    except:
        os.makedirs(ndir)

    p1.to_csv(join(ndir, 'p1.tsv'), sep='\t')
    subbids.to_csv(join(ndir, 'subjects_bids.tsv'), sep='\t')
    encoding.to_csv(join(ndir, 'subjects_memorytask.tsv'), sep='\t')
    npsych.to_csv(join(ndir, 'subjects_npsychresults.tsv'), sep='\t')
    meanmotion.to_csv(join(ndir, 'subjects_meanmotion.tsv'), sep='\t')
    behav.to_csv(join(ndir, 'subjects_mean_retrieval.tsv'), sep='\t')
    
def main():
    fetch_cimaq_data()

if __name__ == "__main__":
    main()
    