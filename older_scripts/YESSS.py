#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 07:48:20 2020

@author: francois
"""
from collections import Counter
import grp
import json
import nibabel as nib
import nilearn as nil
from nilearn import datasets
import numpy as np
import os
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import join
from os.path import isdir
from os.path import splitext
import pandas as pd
from pandas import DataFrame as df
import pwd
import re
import shutil
from shutil import copyfile as cpf
from shutil import copytree as cpt
from shutil import move as mv
from cimaq_utils import flatten
from cimaq_utils import json_read
from cimaq_utils import json_write
from cimaq_utils import loadimages

# oldmsldir = os.path.expanduser('~/cimaq_03-19')
# newmsldir = os.path.expanduser('~/cimaq_20190901')
# mydir = os.path.expanduser('~/CIMAQ_fmri_memory/scans_sorted')

maindir = os.path.expanduser('~/cimaq4prep/cimaq_nov2020_ses-4_nofmaps_filtered_jsonok')
p1 = pd.read_csv(join(maindir, 'participants.tsv'),
                 sep='\t', dtype='object').set_index(
                     'participant_id').sort_index()
# Make BIDS recommended 'task-memory_events.json' descriptive file
task_memory_events = pd.read_excel(
    join(maindir, 'task-memory_events.xlsx')).astype('object').drop(0).set_index('onset').drop(
        columns=['field']).to_json(join(maindir, 'task-memory_events2.json'))
# Add 'Manufacturer' field know eventual Nifti headers labels in advance
# Replace site by institution name to obtain scanner model
# Original site names from
# http://www.cima-q.ca/wp-content/uploads/2018/03/8_Annexe-M_Protocole-CIMA-Q-complet-2.pdf
# p. 19 (Table  Plateformes d’IRM avec protocole validé pour CIMA-Q)
# "CHUM" & "UNF" need to be replaced by "IGM"; "MNI" & "Douglas" by "JGH"
# p1['site'] = p1['site'].replace(map([["CHUM", "UNF"],
#                                           ["MNI", "Douglas"]], ["IGM", "JGH"]))


p1['modalities'] = [ls(join(maindir, row[0], 'ses-4'))
              for row in p1.iterrows()]
p1['anat'] = [ls(join(maindir, row[0], 'ses-4', 'anat'))
              for row in p1.iterrows()]
p1['n_anat'] = [len(row[1]['anat']) for row in p1.iterrows()]
p1['dwi'] = [ls(join(maindir, row[0], 'ses-4', 'dwi'))
              for row in p1.iterrows()]
p1['func'] = [ls(join(maindir, row[0], 'ses-4', 'func'))
              for row in p1.iterrows()]
p1['n_dwi'] = [len(row[1]['dwi']) for row in p1.iterrows()]
p1['n_func'] = [len(row[1]['func']) for row in p1.iterrows()]

# All participants have the same number of files for 'dwi' modality
anat_standard = p1.loc[[row[0] for row in p1.iterrows()
                        if row[1]['n_anat'] == 10]]
anat_tocheck = p1.drop(anat_standard.index)
func_standard = p1.loc[[row[0] for row in p1.iterrows()
                        if row[1]['n_func'] == 5]]
func_tocheck = p1.drop(func_standard.index)

# Participants with more files than most others have had more than a single run
# for certain modalities. Most recent run for each modality are kept,
# others are moved to a clone directory (for merging later).

# Create empty directory structure
clone = sorted(list(dict.fromkeys([dname(img).replace(bname(maindir),
                                                     'cimaq_filter', 1)
                                  for img in loadimages(maindir)
        if bname(img).startswith('sub-')])))
[os.makedirs(item, exist_ok=True) for item in clone]

# List runs for each participant with multiple runs except for each
# participant's most recent run and transfer them to clone repo
p1['multiruns'] = [[(img, join(dname(maindir), img.replace(maindir, 'cimaq_filter', 1)))
                    for img in loadimages(join(maindir, row[0]))
                    if '_run-' in img]
                   for row in p1.iterrows()]
p2 =  p1.loc[[row[0] for row in p1.iterrows()
            if len(row[1]['multiruns']) != 0]]['multiruns']
p2['runs'] = [sorted(list(dict.fromkeys([item[0].split('_run-')[1][:2]
                                         for item in row[1]['multiruns']])))[:-1]
              for row in p2.iterrows()]
# 1st run can be moved for each of these subjects
# Run 02 for sub-8980899 can be transferred too (right after)
run01mover = [item for item in df([[item for item in row[1]['runners']
                                    if '_run-01' in item[0]]
              for row in p2.iterrows()]).values.flat]
run01mover = [item for item in run01mover if isinstance(item, tuple)]
[mv(item[0], item[1]) for item in run01mover]
# sub-8980899
thisguy = [(item, join(dname(maindir), item.replace(maindir, 'cimaq_filter', 1)))
           for item in loadimages(join(maindir, 'sub-8980899'))
           if '_run-02' in item]
[mv(item[0], item[1]) for item in thisguy]
# remove '_run-' prefix in concerned files
with_runs = [(item, re.sub('_run-'+"\d{2}", '', item))
             for item in loadimages(maindir) if '_run-' in item]
[os.rename(item[0], item[1]) for item in with_runs]
###############################################################################

# Assert all subjects have consistent scanning parameters
# Issue arises from T1w, dwi and memory_bold scans (53 files in cause)
# maindir = '~/cimaq4prep/cimaq_nov2020_ses-4_nofmaps_filtered_jsonok'
def uniformize_scanparams(maindir, scanmod):
    # scanmod = str(scanmod)
    maindir = os.path.expanduser(maindir)
    p1 = pd.read_csv(join(maindir, 'participants.tsv'),
                     sep='\t', dtype='object').set_index(
                         'participant_id').sort_index()
    p1[str(scanmod)+'_nib_headers'] = [[dict(nib.load(img).header)
                          for img in loadimages(join(maindir, row[0]))
                          if img.endswith('.nii.gz') and str(scanmod) in img]
                         for row in p1.iterrows()]
    p1[str(scanmod)+'_bids_json'] = [[json.load(open(img))
                          for img in loadimages(join(maindir, row[0]))
                          if img.endswith('.json') and str(scanmod) in img]
                         for row in p1.iterrows()]
    assert len(p1[str(scanmod)+'_nib_headers'].values) ==\
        len(p1[scanmod+'_bids_json'])
    
    bids2nib = df(tuple(zip(p1[str(scanmod)+'_nib_headers'],
                            p1[str(scanmod)+'_bids_json'])),
                  index=p1.index, columns=[str(scanmod)+'_nib_headers',
                                           str(scanmod)+'_bids_json'])
    bids2nib['n_'+scanmod+'_nib_headers'] = [len(bids2nib.loc[row[0]]\
                                              [scanmod+'_nib_headers'])
                                          for row in bids2nib.iterrows()]
    nib_headers = df((pd.Series(item[0]) for item in
                      bids2nib[str(scanmod)+'_nib_headers'].values),
                          index=p1.index)
    bids_json = df((pd.Series(item[0]) for item in
                    bids2nib[str(scanmod)+'_bids_json'].values),
                          index=p1.index)
    return nib_headers, bids_json

# Generate comparative tables and save to tsv
os.mkdir(join(maindir, 'inconsistant_scan_params'))
t1w_nib_headers, t1w_bids_json = uniformize_scanparams(maindir, scanmod='T1w')
dwi_nib_headers, dwi_bids_json = uniformize_scanparams(maindir, scanmod='dwi')
memory_bold_nib_headers, memory_bold_bids_json =\
    uniformize_scanparams(maindir, scanmod='memory_bold')
scan_params_full = ((t1w_nib_headers, 't1w_nib_headers'),
                    (t1w_bids_json, 't1w_bids_json'),
                    (dwi_nib_headers, 'dwi_nib_headers'),
                    (dwi_bids_json, 'dwi_bids_json'),
                    (memory_bold_nib_headers, 'memory_bold_nib_headers'),
                    (memory_bold_bids_json, 'memory_bold_bids_json'))
[item[0].to_csv(join(maindir, 'inconsistant_scan_params', item[1]+'.tsv'),
                sep='\t') for item in scan_params_full]
# Problem arises from Philips Scanners



    # bids2nib['n_str(scanmod)_bids_json'] = [len(bids2nib.loc[row[0]]\
    #                                         ['str(scanmod)_bids_json'])
    #                                     for row in str(scanmod)_bids2nib.iterrows()]
    # bids2nib['n_str(scanmod)_bids_json'] = [len(str(scanmod)_bids2nib.loc[row[0]]\
    #                                         ['str(scanmod)_bids_json'])
    #                                     for row in str(scanmod)_bids2nib.iterrows()]
    # Nifti and json files are homologous in number (1 nib : 1 json)
    p1['dwi_nib_headers'] = [[dict(nib.load(img).header)
                          for img in loadimages(join(maindir, row[0]))
                          if img.endswith('.nii.gz') and 'dwi' in img]
                          for row in p1.iterrows()]
    p1['Memory_bold_headers'] = [[dict(nib.load(img).header)
                          for img in loadimages(join(maindir, row[0]))
                          if img.endswith('.nii.gz') and 'memory_bold' in img]
                          for row in p1.iterrows()]
    p1['dwi_bids_json'] = [[json.load(open(img))
                          for img in loadimages(join(maindir, row[0]))
                          if img.endswith('.json') and 'dwi' in img]
                          for row in p1.iterrows()]
    p1['memory_bold_bids_json'] = [[json.load(open(img))
                          for img in loadimages(join(maindir, row[0]))
                          if img.endswith('.json') and 'memory_bold' in img]
                          for row in p1.iterrows()]


p1['dwi_headers'] = [[dict(nib.load(img).header)
                      for img in loadimages(join(maindir, row[0]))
                      if img.endswith('.nii.gz') and 'dwi' in img]
                       for row in p1.iterrows()]
p1['memory_bold_headers'] = [[dict(nib.load(img).header)
                              for img in loadimages(join(maindir, row[0]))
                              if img.endswith('.nii.gz')
                              and 'memory_bold' in img]
                             for row in p1.iterrows()]        
                     

                     
subjects = df(p1[['pscid', 'dccid']], index=p1.index).sort_index()
# subjects['sub-path'] = [join(maindir, row[0]) for row in subjects.iterrows()]
# subjects['sub-files'] = [loadimages(join(maindir, row[0]))
#                          for row in subjects.iterrows()]
# subjects['folders01'] = [ls(join(maindir, row[0]))
#                                   for row in subjects.iterrows()]
subjects['anat'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'anat' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in subjects.iterrows()]
subjects['dwi'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'dwi' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in subjects.iterrows()]
subjects['fmap'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'fmap' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in subjects.iterrows()]
subjects['func'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'func' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in subjects.iterrows()]
subjects['ses-V01'] = [join(maindir, row[0], 'ses-V01')
                       for row in p1.iterrows()]

os.mkdir('../cimaq_nov2020_sesv01')
ses1dir = os.path.expanduser('~/cimaq_nov2020_sesV01')
[os.makedirs(join(ses1dir, row[0])) for row in subjects.iterrows()]
subjects['new_ses-V01'] = [join(ses1dir, row[0], 'ses-V01') for row in subjects.iterrows()]



ses1mover = tuple(zip(subjects['ses-V01'], subjects['new_ses-V01']))
[mv(item[0], item[1]) for item in ses1mover]

subjects['events'] = [[file for file in loadimages(join(maindir, row[0]))
                      if 'ses-V01' and 'events.tsv' in file][0]
                      for row in subjects.iterrows()]
subjects['new_ses-V03_events'] = [join(dname(file),
                                       bname(os.path.splitext(file)[0])[:11]+\
                                           '_ses-V03_task-memory_events.tsv')
                                  for file in subjects['events']]
    
                      
subjects['new_ses-V04_events'] = flatten([[join(dname(file), row[0]+'_ses-V04_task-memory_events.tsv') for file in loadimages(join(maindir, row[0]))
                      if 'events.tsv' in file]
                      for row in subjects.iterrows()])
subjects['ses4events'] = [[file for file in loadimages(join(maindir, row[0], 'ses-4', 'func'))
                           if '_events' in file][0]
                          for row in subjects.iterrows()]
subjects['newses4events'] = [[file.replace('ses-V04', 'ses-4', -1) for file in loadimages(join(maindir, row[0], 'ses-4', 'func'))
                           if '_events' in file][0]
                          for row in subjects.iterrows()]
subjects['jsonfiles'] = [[(bname(file), json_read(file))
                          for file in loadimages(join(maindir, row[0]))
                         if file.endswith('.json')]
                         for row in subjects.iterrows()]

ev4renamer = tuple(zip(subjects['ses4events'], subjects['newses4events']))
[os.rename(item[0], item[1]) for item in ev4renamer]
[os.rename(item[0], item[1]) for item in subjects['ses4']]
ses3renamer = tuple(zip(subjects['events'], subjects['new_ses-V03_events']))
[cpf(item[0], item[1]) for item in ses3renamer]
ses3events  = [(file, join(maindir, bname(file)[:11], bname(file))) for file in loadimages('/home/francois/cimaq4prep/ses3events')]
[os.rename(item[0], item[1]) for item in ses3events]
ses3renamer = tuple(zip(subjects['events'], subjects['new_ses-V04_events']))


['/home/francois/cimaq4prep/sub-3420680/ses-V04/func/sub-3420680_ses-V04_task-memory_events.tsv', '/home/francois/cimaq4prep/sub-3420680/ses-V01/func/sub-3420680_task-Encoding_run-01_events.tsv']
# [os.makedirs(join(maindir, row[0], 'ses-V03'))
#                        for row in p1.iterrows()]
# subjects['new_ses-V03'] = [join(maindir, row[0], 'ses-V03', 'func')
#                        for row in p1.iterrows()]
# [shutil.rmtree(folder) for folder in subjects['new_ses-V03']]
# ses03renamer = tuple(zip(subjects['ses-V03'], subjects['new_ses-V03']))
# [cpt(item[0], item[1]) for item in ses03renamer]


# [mv(join(maindir, row[0], 'func'), join(maindir, row[0], 'ses-V01', 'func'))
#  for row in subjects.iterrows()]
assert 'ses-4' in subjects['folders01'].all()
assert 'ses-V03' in subjects['folders01'].all()
assert 'anat' in subjects['folders01'].all()
assert 'func' in subjects['folders01'].all()

# [[cpf(join(maindir, row[0], 'ses-V01', 'func', file),
#    join(maindir, row[0], 'ses-V04', 'func', file))
#  for file in ls(join(maindir, row[0], 'ses-V01', 'func'))
#  if 'events' in file]
#  for row in subjects.iterrows()]
ses04 = loadimages(join(maindir, 'ses-V04'))
ses03bold = flatten([[file for file in loadimages(join(maindir, row[0], 'ses-V03'))
               if 'bold' in file] for row in subjects.iterrows()])
ses03newbold = flatten([[join(dname(file), row[0]+'_'+bname(dname(dname(file)))+'_task-memory_bold.') for file in loadimages(join(maindir, row[0], 'ses-V03'))
               if 'bold' in file] for row in subjects.iterrows()])
ses04bold = flatten([[file for file in loadimages(join(maindir, row[0], 'ses-V04'))
               if 'bold' in file] for row in subjects.iterrows()])
ses04newbold = flatten([[join(dname(file), row[0]+'_'+bname(dname(dname(file)))+'_task-memory_bold.tsv') for file in loadimages(join(maindir, row[0], 'ses-V04'))
               if 'bold' in file] for row in subjects.iterrows()])
ses03renamer = tuple(zip(ses03bold, ses03newbold))
ses04renamer = tuple(zip(ses04bold, ses04newbold))
[os.rename(item[0], item[1]) for item in ses03renamer]
[os.rename(item[0], item[1]) for item in ses04renamer]

jsontest = pd.read_excel('/home/francois/CIMAQ_fmri_memory/headers_infos/subjects_bids_headers.xlsx').to_dict()
ses4 = [os.rename(join(maindir, row[0], 'ses-4'), join(maindir, row[0], 'ses-V04')) for row in subjects.iterrows()]
participants_description = json_write(pd.read_excel('/home/francois/CIMAQ_fmri_memory/headers_infos/subjects_bids_headers.xlsx').to_json(),
                                      join(maindir, 'participants_description.json'))



# os.mkdir(os.path.expanduser('~/cimaq_ses-V10'))
# newdir = os.path.expanduser('~/cimaq_ses-V10')
# subjects_v10 = df([(row[0], join(maindir, row[0], 'ses-V10'),
#                     join(newdir, row[0], 'ses-V10'))
#                    for row in subjects.iterrows()
#                    if 'ses-V10' in row[1]['folders01']],
#                   columns=['participant_id', 'ses-V10',
#                            'newpath']).set_index('participant_id').sort_index()
# mover = tuple(zip(subjects_v10['ses-V10'], subjects_v10['newpath']))

# [os.makedirs(join(newdir, ind), exist_ok=True) for ind in subjects.index]
# [mv(item[0], item[1]) for item in mover]



renamefiles = subjects[['sub-files', 'dccid']]
renamefiles['newfiles'] = [json.loads(json.dumps(row[1]['sub-files']).replace('sub-'+row[1]['dccid'], row[0], -1))
                           for row in renamefiles.iterrows()]
renamefiles['renamer'] = [tuple(zip(row[1]['sub-files'], row[1]['newfiles']))
                          for row in renamefiles.iterrows()]
[[os.rename(item[0], item[1]) for item in row[1]['renamer']]
 for row in renamefiles.iterrows()]
renamer = tuple(zip(sorted(renamefiles['sub-files']),
                    sorted(renamefiles['newfiles'])))
renamefiles['sub-dccid'] = [str('sub-'+row[1]['dccid'])
                        for row in renamefiles.iterrows()]
subjects = subjects.drop(columns=['files'])

subjects = subjects.drop(
    index=[row[0] for row in subjects.iterrows()
           if row[1]['pscid'] not in p1['pscid'].tolist()]).drop(
                   columns=['pscid'])
subjects['dccid'] = [row[1]['dccid']
                                  for row in p1.iterrows()]

p1_files2 = df([(item, join(maindir, item), loadimages(join(maindir, item)))
                         for item in ls(maindir)
                         if os.path.isdir(join(maindir, item))
                         and 'sub' in bname(item)],
                        columns=['sub-dccid', 'sub-path', 'files']).set_index('sub-dccid').sort_index()
p1_files2['sub-pscid'] = ['sub-'+row[1]['pscid']
                                   for row in p1.iterrows()]
# uniqueindexes = list(p1_files2.index.unique())
p1_files2['folders01'] = [ls(join(maindir, row[0]))
                                  for row in p1_files2.iterrows()]
p1_files2['pscid'] = [row[0][4:10]
                                  for row in p1_files2.iterrows()]
p1_files2['anat'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'anat' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in p1_files2.iterrows()]
p1_files2['dwi'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'dwi' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in p1_files2.iterrows()]
p1_files2['fmap'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'fmap' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in p1_files2.iterrows()]
p1_files2['func'] = [[item for item in loadimages(join(maindir, row[0]))
                              if 'func' == bname(dname(item))
                              and 'derivatives' not in item]
                              for row in p1_files2.iterrows()]
p1_files2 = p1_files2.drop(columns=['files'])
p1_files2 = p1_files2.drop(
    index=[row[0] for row in p1_files2.iterrows()
           if row[1]['dccid'] not in p1['participant_id'].tolist()]).drop(
                   columns=['dccid'])
p1_files2['dccid'] = [row[1]['dccid']
                                  for row in p1.iterrows()]




p1_files['oldfiles'] = [list(row[1].values.flatten()) for row in p1_files.iterrows()]

p1_files['newfiles'] = [[apath.replace(row[0], 'sub-'+row[1]['pscid'], -1) for apath in row[1]['oldfiles']] for row in p1_files.iterrows()]
p1_files2['newpath'] = [row[1]['sub-path'].replace(row[0], row[1]['sub-pscid'], -1)
                                  for row in p1_files2.iterrows()]
renamer = tuple(zip(p1_files2['sub-path'], p1_files2['newpath']))
[os.rename(item[0], item[1]) for item in renamer]
                   
nil.plotting.plot_img('/home/francois/cimaq_03-19/sub-979001/ses-4/anat/sub-979001_ses-4_T2star.nii.gz', display_mode='tiled')
['anat', 'dwi', 'fmap', 'func']
scandir = join(maindir, 'scans_sorted')
fullevents = [(ef,
               pd.read_csv(ef, sep='\t').fillna("n/a").set_index('onset'))
                        for ef in [ief for ief in
                                   loadimages(scandir)
                                   if 'event' in ief]]
[ef[1].to_csv(ef[0], sep='\t') for ef in fullevents]
fullheaders = [(hf,
               pd.read_csv(hf, sep='\t').fillna("n/a").set_index('header'))
                        for hf in [ihf for ihf in
                                   loadimages(scandir)
                                   if 'nifti1_headers' in ihf]]
p1 = pd.read_csv(join(scandir, 'p12.tsv'), sep='\t')
p1['sub-dccid'] = ['sub-'+str(val) for val in p1['participant_id'].values]
p1['sub-pscid'] = ['sub-'+str(val) for val in p1['pscid'].values]
p1[['ajsonpath_path', 'ajsonpath_file']] = df([(ajsonpath,
                  json.load(open(ajsonpath, "r"))) for ajsonpath in loadimages(msldir)
              if 'dwi.json' in ajsonpath and bname(dname(dname(dname(ajsonpath))))
              in p1.pscid.tolist()]).iterrows()

test = df([(item, join(msldir, item), ls(join(msldir, item))) for item in ls(msldir)
           if os.path.isdir(join(msldir, item)) and 'sub' in item
           and item in p1['sub-pscid'].tolist()],
          columns=['sub-pscid', 'sub-path', 'versions']).set_index('sub-pscid')
# p1 = p1.set_index('participant_id')
rest_json_v03 = [img for img in loadimages]
bold_jsonsv03 = df(((bname(dname(dname(dname(bjson)))), bjson,
                  json.load(open(bjson, "r"))) for bjson in loadimages(msldir)
              if '_bold.json' and 'V03' in bjson and bname(dname(dname(dname(bjson))))
              in p1['sub-pscid'].tolist()),
                columns=['sub-pscid',
                         'fpath', 'json_file']).set_index('sub-pscid')
resttaskv03 = df((row[1] for row in bold_jsonsv03.iterrows()
              if 'rest' in row[1]['fpath']))
memtaskv03 = df((row[1] for row in bold_jsonsv03.iterrows()
              if row[1] not in resttaskv03.iterrows()))
bold_jsonsv10 = df(((bname(dname(dname(dname(bjson)))), bjson,
                  json.load(open(bjson, "r"))) for bjson in loadimages(msldir)
              if '_bold.json' and 'V10' in bjson and bname(dname(dname(dname(bjson))))
              in p1['sub-pscid'].tolist()),
                columns=['sub-pscid',
                         'fpath', 'json_file']).set_index('sub-pscid')
resttaskv10 = df((row[1] for row in bold_jsonsv10.iterrows()
              if 'rest' in row[1]['fpath']))
memtaskv10 = df((row[1] for row in bold_jsonsv10.iterrows()
              if row[1] not in resttaskv03.iterrows()))


anat_jsons = df(((bname(dname(dname(dname(ajson)))), ajson,
                  json.load(open(ajson, "r"))) for ajson in loadimages(msldir)
              if 'T1w.json' in ajson and bname(dname(dname(dname(ajson))))
              in p1['sub-pscid'].tolist()),
                columns=['sub-pscid',
                         'fpath', 'json_file']).set_index('sub-pscid')
anat_json_v03 = df((row[1] for row in anat_jsons.iterrows()
                 if 'V03' in row[1].fpath))
anat_json_v03_doubles = df((row[1]['json_file'] for row in anat_json_v03.iterrows()
                            if '_run' in row[1].fpath), index=[row[0] for row in anat_json_v03.iterrows()
                                                               if '_run' in row[1].fpath])
anat_json_v03_doubles['anat_file'] = [[img for img in loadimages(join(msldir, row[0]))
                                      if 'T1w.nii.gz' and 'V03' in img]
                                      for row in anat_json_v03_doubles.iterrows()]                                                   
anat_json_v10 = df((row[1] for row in anat_jsons.iterrows()
                 if 'V10' in row[1].fpath))
anattest = [bname(dname(dname(dname(ajson[0])))) for ajson in anat_jsons]
ajsonfiles = [json.load(open(fpath, "r")) for fpath in anat_jsons]
# [item[1].to_csv(item[0], sep='\t') for item in fullevents]
incomplete_scans_files = pd.read_excel(join(maindir, 'temp_files/new_important/others/incomplete_scans.xlsx')).set_index('header')
incomplete_scans = sorted(list(pd.read_excel(join(maindir, 'temp_files/new_important/others/incomplete_scans.xlsx')).set_index('header').columns))
incomplete_p1 = p1.loc[[int(part_id[4:])
                                            for part_id in incomplete_scans]]
# incomplete_p1.to_csv(join(maindir, 'scans_sorted', 'incomplete_p1.tsv'), sep='\t')
p1 = p1.drop(index=incomplete_p1.index)
# p1.to_csv(join(maindir, 'scans_sorted', 'p1.tsv'), sep='\t')

# os.mkdir(join(maindir, 'incomplete_scans'))
# [move(join(maindir, 'scans_sorted', incscan), join(maindir, 'incomplete_scans', incscan)) for incscan in incomplete_scans]
bold_json_files = df([(os.path.splitext(bname(ihf))[0],
                        nib.load(ihf).header.get_zooms()[3])
                       for ihf in loadimages(join(maindir, 'scans_sorted'))
                       if 'bold.nii' in ihf],
                      columns=["participant_id",
                               "RepetitionTime"]).set_index('participant_id')
bold_json_files['scan_duration'] = [item[1]['offset'].iloc[item[1].shape[0]-1]
                                    for item in fullevents]
bold_json_files['image_dimensions'] = [nib.load(ihf).header.get_data_shape()
                       for ihf in loadimages(join(maindir, 'scans_sorted'))
                       if 'bold.nii' in ihf]
bold_json_files['AcquisitionTime'] = [item[1].loc['descrip'].values
                                      for item in fullheaders]
bold_json_files['MagneticFieldStrength'] = 3.0
bold_json_files['EchoTime'] = bold_json_files['RepetitionTime']/2
bold_json_files['TaskName'] = "Encoding"
# oldnames = [item for item in loadimages(join(maindir, 'scans_sorted'))
#             if item.endswith('events.tsv')]
# newnames = [join(dname(item), os.path.splitext(bname(item))[0][:10]+'_task-Encoding_run-01_events.tsv')
#             for item in oldnames]
# renamer = tuple(zip(sorted(oldnames), sorted(newnames)))
# [os.rename(item[0], item[1]) for item in renamer]


def make_bids(encdf):
    maindir = os.path.expanduser('~/CIMAQ_fmri_memory')
    datadir = join(maindir, 'data_sorted')

    # encdf = pd.read_excel(join(datadir, 'enc_df.xlsx'))
    enc_dir = join(maindir, 'data/task_files/processed/memory_events')
    encfiles = dict(sorted(
        [(mtask_file[4:10], pd.read_csv(
            join(enc_dir, mtask_file), sep='\t').drop(
                ['trial_number'], axis=1).transpose())
                for mtask_file in ls(enc_dir)]))
    os.mkdir(join(maindir, 'data_sorted/enc_events_dir'))
    [item[1].to_csv(join(maindir, 'data_sorted/enc_events_dir',
                         'sub-'+item[0]+'_events'+'.tsv'), sep='\t')
     for item in encfiles.items()]
    # retdf = pd.read_excel(join(datadir, 'ret_df.xlsx'))
    ret_dir = join(maindir, 'data/task_files/processed/PostScanBehav')
    retfiles = dict(sorted(
        [(os.path.splitext(pscan_file.split('PostScanBehav_pscid')[1])[0][-6:],
          pd.read_csv(join(ret_dir, pscan_file), sep='\t').drop(
              ['trial_number'], axis=1).transpose())
         for pscan_file in ls(ret_dir)]))
    os.mkdir(join(maindir, 'data_sorted/ret_events_dir'))
    [item[1].to_csv(join(maindir, 'data_sorted/ret_events_dir',
                         'sub-'+item[0]+'_events_ret_'+'.tsv'), sep='\t')
     for item in retfiles.items()]
    
    npsy_tables = list((splitext(fname),
                        pd.read_excel(join(datadir, 'npsy_tables', fname)))
                       for fname in ls(join(datadir, 'npsy_tables')))
    npsy_subtests = list((splitext(fname),
                          pd.read_excel(join(datadir, 'npsy_subtests', fname)))
                         for fname in ls(join(datadir, 'npsy_subtests')))
    npsy_scores = pd.read_excel(join(datadir, 'npsy_scores.xlsx'))
    ret_task_all_subs = pd.read_excel(join(datadir, 'ret_task_all_subs.xlsx'))
    ret_scores = pd.read_excel(join(datadir, 'ret_scores.xlsx'))
    sub_scans = pd.read_excel(join(datadir, 'subjects_scans.xlsx'))
    sub_scans.index = sub_scans.index.map(int)

    enc_events = df([(evfile[11:17],
                      join(maindir, 'data_sorted/enc_events_dir', evfile))
                        for evfile in ls(join(maindir,
                                              'data_sorted/enc_events_dir'))],
                       columns=['dccid',
                                'event_path']).set_index('dccid').sort_index()
    enc_events.index = enc_events.index.map(int)
    enc_events2 = enc_events.loc[sub_scans.index]

    assert all(sub_scans.index) == all(enc_events2.index)
    sub_scans2 = pd.concat([sub_scans,
                                    enc_events2], axis=1)
    sub_scans3 = sub_scans2[['fmri_path', 'anat_path', 'event_path']]

    [os.makedirs(join(maindir, 'scans_sorted',
                      'sub-'+str(ind)), exist_ok=True) 
                 for ind in sub_scans.index]
    [os.makedirs(join(maindir, 'scans_sorted',
                      'sub-'+str(ind), 'anat'), exist_ok=True) 
                 for ind in sub_scans.index]
    [os.makedirs(join(maindir, 'scans_sorted',
                      'sub-'+str(ind), 'func'), exist_ok=True) 
                 for ind in sub_scans.index]
    [copyfile(apath[1], join(maindir, 'scans_sorted',
                             'sub-'+str(apath[0]), 'anat', bname(apath[1])))
     for apath in sub_scans3['anat_path'].items()]
    headers = [(bname(dname(dname(file))), pd.read_csv(file, sep='\t'))
               for file in [nhead for nhead in loadimages(join(maindir,
                                                               'scans_sorted'))
                            if 'nifti1_header' in nhead]]
    [os.rename(fpath[1], join(maindir, 'scans_sorted',
                              'sub-'+str(fpath[0]), 'func', bname(fpath[1])))
          for fpath in sub_scans3['fmri_path'].items()]
    # [copyfile(fpath[1], join(maindir, 'scans_sorted',
    #                           'sub-'+str(fpath[0]), 'func', bname(fpath[1])))
    #       for fpath in sub_scans3['fmri_path'].items()]

    bold_example = pd.read_json('/home/francois/CIMAQ_fmri_memory/bids_examples_ds003345/func/sub-21134_func_sub-21134_task-PenaltyKik_run-01_bold.json')
    bold_example.to_csv('/home/francois/CIMAQ_fmri_memory/bids_examples_ds003345/func/sub-21134_func_sub-21134_task-PenaltyKik_run-01_bold.tsv', sep='\t')
    anatfiles = dict((bname(dname(dname(img))), json.dumps(dict((item[0], str(np.array(item[1]).view())) for item in nib.load(img).header.items()), indent=0)) for img in loadimages(join(maindir, 'scans_sorted'))
                if 'T1w' in bname(img))
    anatfiles = dict((bname(dname(dname(img))), dict((item[0], str(np.array(item[1]).view())) for item in nib.load(img).header.items())) for img in loadimages(join(maindir, 'scans_sorted'))
                if 'T1w' in bname(img))
    anatdf = df.from_dict(anatfiles, orient='index')
    anatdf.to_csv(join(maindir, 'scans_sorted', 'anat_headers.tsv'), sep='\t')
    anatfiles2 = json.dumps(anatfiles, indent=0)
    
    
    funcfiles2 = dict((bname(dname(dname(img))), dict((item[0], np.array(item[1]).view()) for item in nib.load(img).header.items())) for img in loadimages(join(maindir, 'scans_sorted'))
                if '_run' in bname(img))
    
    json_write(str(funcfiles), join(maindir, 'scans_sorted', 'nifti_headers.json'), idt=16)
    test = json.load(os.path.relpath(join(maindir, 'scans_sorted', 'nifti_headers.json')))
    
    test2=df.from_dict(test)
    test2.to_csv(join(maindir, 'scans_sorted', 'nifti_headers.tsv'), sep='\t')
    test2 = json_read(join(maindir, 'scans_sorted', 'nifti_headers.json'))
    test2 = json.dumps(test, indent=4)
    json_write(test2, join(maindir, 'scans_sorted', 'nifti_headers2.json'))

    test = json.dumps(funcfiles)
    funcfiles = df(((bname(dname(dname(img))), list(item for item in nib.load(img).header.items())) for img in loadimages(join(maindir, 'scans_sorted'))
                if '_run' in bname(img)))
    funcfiles[1] = []
    funcfiles['fdatas'] = [img.get_fdata() for img in funcfiles.sub]
    newnames = [join(dname(funcfile), 'sub-'+splitext(bname(funcfile))[0][8:14]+'_run-01_'+'bold.nii')
                for funcfile in funcfiles]
    anatfiles = [img for img in loadimages(join(maindir, 'scans_sorted'))
                if 'stereo' in bname(img)]
    newanat = [join(dname(anatfile), 'sub-'+splitext(bname(anatfile))[0][8:14]+'_T1w.nii')
                for anatfile in anatfiles]
    anat_renamer = tuple(zip(anatfiles, newanat))
    [os.rename(item[0], item[1]) for item in anat_renamer]
    evfiles = [img for img in loadimages(join(maindir, 'scans_sorted'))
                if 'sub-ub-' in bname(img)]
    newevents = [join(dname(evfile), bname(dname(dname(evfile)))+'_events.tsv')
                for evfile in evfiles]
    evrenamer = tuple(zip(evfiles, newevents))
    [os.rename(item[0], item[1]) for item in evrenamer]
    func_renamer = tuple(zip(funcfiles, newnames))

    dataset_description = json_write(json.dumps(
        {'Abstract': 'This research aims to train an artificial deep\
                      neural network to identify predictive brain\
                      activity patterns during stimuli encoding for\
                      delayed success or failure of long-term memory\
                      of images representing objects and animals and\
                      their display position.',
         'Authors': {'0': 'Nadeau Francois',
                     '1': 'St-Laurent Marie',
                     '2': 'Belleville Sylvie et al (2018)',
                     '3': 'Bellec Pierre'},
         'BIDSVersion': {'0':'1.1.0'},
         'Name': {'0':'''Predicting offline delayed retrieval from
                    brain activation during stimuli encoding'''},
         'License': 'MIT License, Copyright (c) 2019 courtois-neuromod',
         'References': '''"Belleville, S. et al. (2019)",
                           "The Consortium for the early
                           identification of Alzheimer’s disease–Quebec,
                           (CIMA-Q)",
                           "DOI: 10.1016/j.jalz.2014.05.1606"'''}),\
        fpath=join(maindir, 'scans_sorted', 'dataset_description.json'), idt=4)
    copyfile(join(maindir, 'README.md'),
                   join(maindir, 'scans_sorted', 'README'))
    bold = nib.load('/home/francois/CIMAQ_fmri_memory/scans_sorted/sub-189005/func/fmri_sub189005_sess4_run1_n.nii')
    bold_data = bold.get_fdata()
    bold_headers = dict(bold.header.items())
    