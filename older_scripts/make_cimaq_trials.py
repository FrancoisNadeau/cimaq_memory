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

def make_cimaq_trials():
    p1 = pd.read_csv('./fetched_cimaq/p1.tsv', sep='\t')
    for row in p1.iterrows():
        encsheet = pd.read_csv(row[1]['events'],
                                      sep='\t').drop('Unnamed: 0', axis=1)
        retsheet = pd.read_csv(row[1]['retrieval'],
                               sep='\t').drop('Unnamed: 0', axis=1)
#         ctlsheet = encsheet.where(encsheet.Condition == 0)
#         retsheet['Spatial_RT'] = retsheet['Spatial_RT'].values/1000
#         encsheet['trialDur'] = encsheet['fixDurSec'] + encsheet['stimDurSec']
#         encsheet['isi'] = encsheet['stimOnsetSec'].diff()
#         encsheet['isiFix'] = encsheet['fixOnsetSec'].diff()
#         encsheet['trial_end'] = encsheet.trialDur + encsheet.stimOnsetSec
#         encsheet['unscanned'] = encsheet.trial_end >= \
#                                 nib.load(row[1]['func']).header.get_zooms()[3] * \
#                                 dict(nib.load(row[1]['func']).header)['dim'][4]
        memsheet = pd.merge(encsheet, retsheet, left_on='ImageID',
                        right_on='OldNumber').set_index('tNumXcond', drop=False)
        toscrub = memsheet.where(memsheet.unscanned).dropna()
        memsheet = memsheet.drop(toscrub.index)
 
        # Score calculation
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
        encsheet = memsheet[encsheet.columns]
        encsheet = encsheet.rename(columns={'stimOnsetSec':'onset',
                                            'trialDur': 'duration',
                                            'tNumXcond': 'trial_type'})
        encsheet = encsheet.set_index('trial_num').drop('Condition', axis=1)
        ctlsheet = ctlsheet.rename(columns={'stimOnsetSec':'onset',
                                            'trialDur': 'duration',
                                            'tNumXcond': 'trial_type'})
        memsheet = memsheet[['trial_num', 'hit', 'rejOk', 'recogOkSrcMiss',
                             'miss', 'recogMissSrcOk']]
        memsheet = memsheet.set_index('trial_num', drop=False)
        ctlsheet = ctlsheet.dropna().drop(['Condition', 'ImageID'],
                                          axis=1)
        ctlsheet['trial_num'] = [int(tnum) for tnum
                                 in ctlsheet.trial_num]
        ctlsheet = ctlsheet.set_index('trial_num')
        
        memsheet.to_csv(join(xpu('~/./cimaq_events2020'), row[1]['sub-pscid'],
                             'Outcomes_enc_trials.tsv'), sep='\t')
        encsheet.to_csv(join(xpu('~/./cimaq_events2020'), row[1]['sub-pscid'],
                             'Enc_trials_only.tsv'), sep='\t')
        ctlsheet.to_csv(join(xpu('~/./cimaq_events2020'), row[1]['sub-pscid'],
                             'Ctl_trials_only.tsv'), sep='\t')
def main():
    make_cimaq_trials()

if __name__ == "__main__":
    main()
