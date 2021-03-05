#!/usr/bin/env python3

import chardet
import csv
import glob
import json
import os
import re
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import re
import scipy
import shutil
import sys
import time
import zipfile

from chardet import detect
from chardet.universaldetector import UniversalDetector as udet
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
from os.path import splitext
from pandas import DataFrame as df
from tqdm import tqdm
from cimaq_utils import flatten
from cimaq_utils import loadimages
from cimaq_utils import get_encoding

from cimaq_utils import flatten
from cimaq_utils import get_encoding
from cimaq_utils import loadimages

# def loadpaths(cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'):
# #     cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
#     cimaq_dir = xpu(cimaq_dir)
#     spaths = df(((sub, [itm for itm in sorted(loadimages(join(cimaq_dir,
#                                               'extracted_eprimes2021', sub)))
#                             if 'CIMAQ' in bname(itm) and '._' not in itm])
#                   for sub in ls(join(cimaq_dir,
#                                      'extracted_eprimes2021'))),
#                 columns=['subdccid', 'allpaths']).set_index('subdccid')
#     prefixes = list(dict.fromkeys([bname(str(itm)).split("CIMAQ", 1)[0]
#                                    for itm in flatten(spaths.values.tolist())
#                                    if 'CIMAQ' in bname(itm) \
#                                    and '._' not in itm]))
#     prefixes = sorted(prefixes)
#     spaths[prefixes] = [val[0] for val in spaths.values]
#     spaths = spaths[prefixes]
#     spaths['dccid'] = [ind.split('sub')[1] for ind in spaths.index]
#     spaths['pscid'] = [bname(row[1][prefixes[0]]).split('_')[2]
#                        for row in spaths.iterrows()]
#     return spaths, prefixes
    
# def getid(sheet):
#     nameparts = [str(item) for item
#                  in os.path.splitext(bname(sheet))[0].split("_")]
#     subid = "sub-"+str(nameparts[nameparts.index(\
#                  (item for item in nameparts
#                   if item.isnumeric()).__next__())])
#     return subid

# def makename(sheet, prefixes):
#     if prefixes[0] in sheet:
#         return join(dname(sheet),
#                     bname(dname(sheet))+"_task-memory_events_onset"+".tsv")
#     if prefixes[1] in sheet:
#         return join(dname(sheet),
#                     bname(dname(sheet))+"_task-memory_events_output"+".tsv")
#     if prefixes[2] in sheet:
#         return join(dname(sheet),
#                     bname(dname(sheet))+"_task-Retrieval"+".tsv")
#     else:
#         print("python no compute: " + sheet)

# def get_enc_onsets():
#     # Names from M. St-Laurent (2019)
#     EncOnsetCols = ["TrialNum", "Condition", "TrialNum_perCondi",
#                     "ImageID", "Trial_part", "onsetSec", "durationSec"]
#     frame, prefixes = loadpaths()
#     sheets = frame.iloc[:,0]
#     s_ids, yallofems = [], []
#     for sheet in sheets:
#         nsheet = pd.read_fwf(sheet,
#                              encoding=get_encoding(sheet)[1]['encoding'],
#                              header=None, sep='\t',
#                              names=EncOnsetCols).fillna(False).iloc[6:]

#         stimids = nsheet[["ImageID",
#                           "TrialNum_perCondi"]].drop_duplicates(
#                           subset=["ImageID",
#                                   "TrialNum_perCondi"]).reset_index(drop=True)
#         s_ids.append((bname(sheet[0]), stimids))
#         nsheets = nsheet.drop(['TrialNum_perCondi', 'Condition'], axis=1)
#         tempsheet = nsheet[['TrialNum', 'Trial_part',
#                             'onsetSec', 'durationSec']]
#         # Extract & concatenate relevant info
#         fixsh = df([sheet[1] for sheet in tempsheet.iterrows()
#                        if sheet[1]['Trial_part'] == 'Fixation'])
#         tmng = tempsheet.loc[[sheet[0]
#                                 for sheet in tempsheet.iterrows()
#                                 if sheet[0] not in fixsh.index]]
#         fixsh = fixsh.rename(columns={"onsetSec": "fixOnsetSec",
#                                             "durationSec": "fixDurSec"})
#         fixsh = fixsh.transpose().iloc[-2:].transpose().reset_index(drop=True)
#         tmng = tmng.rename(columns={"onsetSec": "stimOnsetSec",
#                                         "durationSec": "stimDurSec"})
#         tmng = tmng.transpose().iloc[-2:].transpose().reset_index(drop=True)
#         allofem = pd.concat([tmng, fixsh, stimids], axis=1, sort=False)
#         allofem = allofem.rename(columns={"TrialNum_perCondi": "tNumXcond"})
#         enconsTuple = (makename(sheet, prefixes), allofem)
#         yallofems.append(enconsTuple)
#     return sorted(yallofems)

# def get_enc_outputs():
#     encsheets = []
#     frame, prefixes = loadpaths()
#     sheets = frame.iloc[:,1]
#     for sheet in sheets:
#         encsheet = pd.read_csv(sheet,
#                                encoding=get_encoding(sheet)[1]['encoding'],
#                                header=0, sep='\t').fillna(False).rename(
#             columns={"TrialNumber": "TrialNum",
#                      "Category": "Condition"}).iloc[3:]
#         encsheet = encsheet.set_index("TrialNum")
#         # Drop duplicate columns with enc_onset's
#         encsheet = encsheet.drop(["TrialCode", "OldNumber",
#                                   "Stim_RESP"], axis=1)
#         encsheet["Condition"] = encsheet["Condition"].astype('str')
#         # Convert ms to s (as are all other time measures)
#         encsheet["Stim_RT"] = [val/1000 for val in encsheet["Stim_RT"]]
#         encsheet = encsheet.drop(["Stim_ACC"], axis=1)
#         encsheet = encsheet.reset_index(drop=True)
#         encoutTuple = (makename(sheet, prefixes), encsheet)
#         encsheets.append(encoutTuple)
#     return sorted(encsheets)

# def get_ret_outputs():
#     frame, prefixes = loadpaths()
#     sheets = frame.iloc[:,2]
#     retsheets = []
#     for sheet in sheets:
#         # Removing last column as an Eprime error occured (St-Laurent, 2019)
#         retsheet = pd.read_csv(sheet,
#                                encoding=get_encoding(sheet)[1]['encoding'],
#                                header=0, sep='\t').fillna(False).iloc[:, :-1]
#         retsheet["Recognition_RT"] = [float(val)/1000 for val
#                                       in retsheet["Recognition_RT"]]
#         retTuple = (makename(sheet, prefixes), retsheet)
#         retsheets.append(retTuple)
#     return sorted(retsheets)
#     return sheets

# # def megamerge(dflist, merge_on, howto):
# #     return reduce(lambda x, y: pd.merge(x, y,
# #                                         on=merge_on,
# #                                         how=howto).astype('object'),
# #                   dflist)

# def loadmeansheets(cimaq_dir):
# #     cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
#     failedQC = [str(ind) for ind in pd.read_csv(join(xpu(cimaq_dir),
#                                 'memoTask_ParticipantFile.tsv'),
#                            sep='\t').dropna()[['dccid']].set_index('dccid').index]
#     meansheets = df.from_dict(dict((bname(itm).split('_')[0],
#                                     (itm, pd.read_csv(itm,
#                                                       sep='\t', dtype='object').dropna()))
#                                    for itm in sorted(loadimages(join(xpu(cimaq_dir),
#                                                                      'meansheets')))),
#                               orient='index', columns=['paths', 'sheets'])
#     meansheets.sheets.meanMotion = meansheets.sheets.meanMotion.rename(
#         columns={'total_scrubbed': 'total_scrubbed_frames'})
#    # Check fMRI data availability per subject
#     meansheets.sheets.bids['fMRI'] = meansheets.sheets.bids['fMRI'].replace(
#         {'yes': True, not 'yes': False})
#     meansheets.sheets.bids = meansheets.sheets.bids.where(
#         meansheets.sheets.bids.fMRI == True)
#     meansheets2 = megamerge([sheet.dropna() for sheet in meansheets.sheets],
#                             merge_on = 'dccid', howto='inner')
#     meansheets.sheets = [meansheets2[[col for col in sheet.columns
#                                       if col in meansheets2.columns]].dropna().set_index('dccid')
#                          for sheet in meansheets.sheets]
# #     p1 = pd.read_csv(join(xpu(cimaq_dir), 'meansheets', 'taskpaths_participants.tsv'), sep='\t')
#     return meansheets

# def loadpaths(datadir='CIMAQ_fmri_memory_data_neuromod_DATA/data'):
#     cimaq_dir='~/../../media/francois/seagate_8tb/cimaq_03-19_data_simexp_DATA'
#     cimaq_dir = xpu(cimaq_dir)
#     test = pd.Series([bname(itm) for itm
#                       in ls(join(xpu(cimaq_dir), datadir))]).unique()
#     test2 = [itm for itm in loadimages(join(xpu(cimaq_dir), datadir))
#              if 'sub' in itm]
#     test3 = pd.Series([bname(itm).split('_')[1] for itm in test2]).unique()
#     test4 = df([[[itm for itm in test2 if att in itm][0]
#                  for sub in test3] for att in test],
#                index=test, columns=test3).T
#     test4['dccid'] = [ind.split('sub')[1] for ind in test4.index]
#     return test4.dropna()

# def makeindexes():
#     meansheets = loadmeansheets()
#     datas = loadpaths()
#     mtmpindx = [itm for itm in loadmeansheets().sheets.behav.astype('object').index
#                 if itm in datas.dccid.values]
#     return mtmpindx



# def loadinfos2():
#     meansheets = loadmeansheets()
#     datas = loadpaths()
#     datas['subdccid'] = datas.index
#     uindx = makeindexes()
#     datas = datas.set_index('dccid', drop=False).loc[uindx]
#     datas = datas.set_index('subdccid')
#     subinfos = df(((subject, df(((row[0], row[1]['sheets'].loc[subject])
#                      for row in meansheets.iterrows()),
#                     columns=[subject, 'infos']).iloc[:3,].T) 
#                      for subject in uindx),
#                  columns=['dccid', 'mean_datas']).set_index('dccid')
#     return pd.merge(subinfos, datas, on='dccid').set_index('dccid')


