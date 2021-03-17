#! /usr/bin/env python

import os
import pandas as pd
import numpy as np
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join as pjoin
from os import listdir as ls
from pandas import DataFrame as df
from typing import Union
from tqdm import tqdm

from bidsify_utils import bidsify_load_scans
from bidsify_utils import bidsify_names
from scanzip import scanzip
import sniffbytes as snif

def xtrct_cimaq(cimaq_dir: Union[str, os.PathLike]) -> np.ndarray:
    return df(tuple(scanzip(apath,
                            exclude = ['Practice', 'Pratique',
                                       'PRATIQUE', 'PRACTICE', 'READ',
                                       'Encoding-scan', 'Retrieval-'],
                            to_xtrct = ['.pdf', '.edat2'],
                            dst_path = pjoin(os.getcwd(), 'newdevs',
                                             'cimaq_uzeprimes'))
                    for apath in
                    tqdm(snif.filter_lst_inc(snif.clean_bytes(
                        xpu(pjoin(cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
                                  'participants/sub_list_TaskQC.tsv'))).decode(
                        ).split()[1:], snif.loadimages(xpu(pjoin(
                        cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
                        'task_files/zipped_eprime')))))),
             dtype = object)[0].values.flat

def fix_cimaq(cimaq_dir: Union[str, os.PathLike]) -> None:
    os.makedirs(pjoin(os.getcwd(), 'newtest', 'events'), exist_ok = True)
    os.makedirs(pjoin(os.getcwd(), 'newtest', 'behavioural'), exist_ok = True)
    os.makedirs(pjoin(os.getcwd(), 'newdevs', 'cimaq_uzeprimes'), exist_ok = True)
    for val in tqdm(xtrct_cimaq(cimaq_dir), 'fixing cimaq'):
        # creating events files
        (pd.concat([snif.bytes2df(val['bsheets'].values[1],
                                  has_header = None),
                    snif.bytes2df(val['bsheets'].values[0]).loc[:snif.bytes2df(
                        val['bsheets'].values[1],
                        has_header = None).shape[0] -1, :].drop(
                        columns = [0,1,2,3, 4, 6],
                        index = 0).rename(columns = {5: 'onset',
                                                     7: 'fix_onset',
                                                     8: 'fix_duration'})],
                   axis = 1).to_csv(pjoin(os.getcwd(), 'newtest', 'events', 'sub-_' + \
                                          '_'.join(val['filename'].values[0].replace('-', '_').split(
            '_')[:2])+'_run-01_task-encoding_events.tsv'), sep = '\t', index = None),
         # creating behavioural files
         snif.bytes2df(val['bsheets'].values[2], has_header = True).to_csv(pjoin(
             os.getcwd(), 'newtest', 'behavioural', 'sub-_' + '_'.join(
                 val['filename'].values[0].replace('-', '_').split('_')[:2]) + \
                 '_run-01_task-encoding_behavioural.tsv'), sep = '\t', index = None))

def cimaq2nilearn(cimaq_dir: Union[str, os.PathLike]) -> None:
    fix_cimaq(cimaq_dir)
    events = snif.loadfiles(snif.loadimages(pjoin(
                           os.getcwd(), 'newtest', 'events')))
    os.makedirs(pjoin(os.getcwd(), 'newtest', 'nilearn_events'), exist_ok = True)
    for row in tqdm(events.iterrows(), desc = 'conforming events.tsv files'):
        sheet = pd.read_csv(row[1].fpaths, sep = '\t')
        
        sheet['duration'] = sheet['onset'] + \
                                    sheet['fix_duration'] + \
                                    sheet['onset'].sub(
                                    sheet['fix_onset']).round(0)
        sheet.rename(columns = {'category': 'trial_type'}).set_index(
            'trialnumber').to_csv(pjoin(os.getcwd(), 'newtest',
                                        'nilearn_events', row[1].filename + '.tsv'),
                                  sep = '\t', index = None)

def fetch_cimaq(cimaq_dir: Union[str, os.PathLike]) -> dict:
    cimaq2nilearn(cimaq_dir)    
    scan_infos = bidsify_load_scans(cimaq_dir, snif.clean_bytes(xpu(pjoin(
            cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
            'participants/sub_list_TaskQC.tsv'))).decode().split()[1:])

    scan_infos['dccid'] = sorted([(filename, filename.split('-')[1].split('_')[0])[1]
                                  for filename in scan_infos.filename])
    behav = snif.loadfiles(snif.loadimages(pjoin(
                           os.getcwd(), 'newtest', 'behavioural')))
    behav[['pscid', 'dccid']] = [filename.split('_')[1:3]
                                  for filename in behav.filename]
    events = snif.loadfiles(snif.loadimages(pjoin(
                           os.getcwd(), 'newtest', 'nilearn_events')))
    events[['pscid', 'dccid']] = [filename.split('_')[1:3]
                                  for filename in events.filename]

    confounds = snif.loadfiles(snif.filter_lst_inc(
        snif.clean_bytes(xpu(pjoin(cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
                                   'participants/sub_list_TaskQC.tsv'))).decode().split()[1:],
        snif.loadimages( pjoin(cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
                                  'confounds', 'resample'))))
    confounds['bids_names'] = [bidsify_names(filename) for
                               filename in confounds.filename]
    
    subs = df(((grp, scan_infos.groupby('dccid').get_group(grp))
               for grp in tqdm(scan_infos.groupby('dccid').groups,
                               desc = 'loading subjects')),
              columns = ['subject', 'scans']).set_index(
                            'subject').sort_index().reset_index(
                         drop = False)
    return dict(zip(['scans', 'behavior', 'confounds', 'events'],
                    [subs, behav, confounds, events]))

def main():    
    if __name__ == "__main__":
        fetch_cimaq(cimaq_dir)
