#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import glob
import nibabel
import nilearn
import numpy as np
import os
import pandas as pd
import scipy
import sys

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
from os.path import join
from pandas import DataFrame as df
from cimaq_utils import loadimages
from pandas import DataFrame as df

"""
Overview:
Conversion from Nistats to Nilearn
Added optional 'savefiles' argument to allow user to overwrite files to disk or not
"""

def get_new_events(taskfilesdir= "~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/processed",
                   outTask_dir="~/cimaq_memory/NEW_task_files",
                  savefiles=False):
    ''' 
        Create BIDS compliant "_task-memory_events.tsv" from files outputed by "eprime2events.py"
        
        Parameters
        ----------
            taskfilesdir ("str"): Path to input folder as string.
                                  Should not be edited unless files are moved in the datbase.
            outTask_dir ("str"):  Path to output folder.
            
            savefiles ("bool"):   Default=False
                                  If True, saves newly created files to disk in "outTask_dir"
                                  as ".tsv" files. If "outTask_dir" is not empty,
                                  overwites any file with matching name.
        Returns
        -------
            newvents: ("list")
            all_events: ("list")
    '''
          
    taskfilesdir = os.path.expanduser(taskfilesdir)
    outTask_dir = os.path.expanduser(outTask_dir)
    #rename "trial_type" column as "condition"
    taskfiles = [(os.path.splitext(bname(file))[0], pd.read_csv(join(taskfilesdir, file), sep='\t'))
                 for file in ls(taskfilesdir) if "events" in file and file.endswith(".tsv")]
    new_events = []

    for s_task in taskfiles:
    #load counfounds file as pandas dataframe 
    # confounds = pd.read_csv(subject_motion, sep='\t')
    #scan duration, in seconds : number of fMRI frames (~310), times TR = 2.5s
    # scanDur = confounds.shape[0]*2.5
        scanDur = s_task[1].shape[0]*2.5

        s_task[1].rename(columns={'trial_type':'condition'}, inplace=True)

        #add columns to DataFrame
        numCol = s_task[1].shape[1] 
        insertCol = [4, numCol+1, numCol+2, numCol+3]
        colNames = ['trial_type', 'unscanned', 'ctl_miss_hit', 'ctl_miss_ws_cs']
        colVals = ['TBD', 0, 'TBD', 'TBD']
        for i in range(0, len(colNames)):
            s_task[1].insert(loc=insertCol[i], column=colNames[i], value=colVals[i], allow_duplicates=True)

        #The 'unscanned' column flag trials for which no brain data was acquired.
        #The scan's duration is shorter than the trial's offset time
        #(0 = data, 1 = no data)
        for j in s_task[1][s_task[1]['offset']>scanDur].index:
            s_task[1].loc[j, 'unscanned']=1

        #pas trial numbers with zeros (on the left) to preserve trial 
        #temporal order when trials are alphabetized
        s_task[1]['trial_number'] = s_task[1]['trial_number'].astype('object',
                                                               copy=False)
        for k in s_task[1].index:
            s_task[1].loc[k, 'trial_number'] = str(s_task[1].loc[k, 'trial_number']).zfill(3)

        #trial_type should have a unique entry per row so that each trial 
        #can be modelled as a separate condition
        countEnc = 0
        countCTL = 0
        for m in s_task[1][s_task[1]['condition']=='Enc'].index:
            countEnc = countEnc + 1
            s_task[1].loc[m, 'trial_type'] = 'Enc'+str(countEnc)
            if s_task[1].loc[m, 'position_accuracy'] == 0:
                s_task[1].loc[m, 'ctl_miss_hit']='missed'
                s_task[1].loc[m, 'ctl_miss_ws_cs']='missed'
            elif s_task[1].loc[m, 'position_accuracy'] == 1:
                s_task[1].loc[m, 'ctl_miss_hit']='hit'
                s_task[1].loc[m, 'ctl_miss_ws_cs']='wrongsource'
            elif s_task[1].loc[m, 'position_accuracy'] == 2:
                s_task[1].loc[m, 'ctl_miss_hit']='hit'
                s_task[1].loc[m, 'ctl_miss_ws_cs']='correctsource' 
        for n in s_task[1][s_task[1]['condition']=='CTL'].index:
            countCTL = countCTL + 1
            s_task[1].loc[n, 'trial_type'] = 'CTL'+str(countCTL)
            s_task[1].loc[n, 'ctl_miss_hit']='control'
            s_task[1].loc[n, 'ctl_miss_ws_cs']='control'

        #78 encoding and 39 control trials if full scan
        print('Number of encoding trials:  ', countEnc)
        print('Number of control trials:  ', countCTL)



        #keep only trials for which fMRI data was collected
# #        s_task[1] = s_task[1][s_task[1]['unscanned']==0]

        s_task[1]['unscanned'] = 0

        #Save vectors of trial labels (e.g., encoding vs control)
        #to label trials for classification analyses
        ttypes1 = s_task[1]['condition']

        ttypes2 = s_task[1]['ctl_miss_hit']

        ttypes3 = s_task[1]['ctl_miss_ws_cs']

        new_events.append([(s_task[0], s_task[1]), ttypes1, ttypes2, ttypes3])
        
# Allows user to overwrite files to disk or not 
        if savefiles == True:
                    #Export Dataframe to events.tsv file    
            s_task[1].to_csv(outTask_dir+'/sub-'+id+'_events.tsv',
                          sep='\t', header=True, index=False)
            ttypes1.to_csv(outTask_dir+'/sub-'+id+'_enco_ctl.tsv',
                           sep='\t', header=True, index=False)
            ttypes2.to_csv(outTask_dir+'/sub-'+id+'_ctl_miss_hit.tsv',
                           sep='\t', header=True, index=False)
            ttypes3.to_csv(outTask_dir+'/sub-'+id+'_ctl_miss_ws_cs.tsv',
                           sep='\t', header=True, index=False)

    #from s_task[1] dataframe, create an events dataframe to create a design matrix 
    #that will be inputed into a first-level model in nistats
    ev_cols = ['onset', 'duration', 'trial_type', 'condition', 'ctl_miss_hit', 
               'ctl_miss_ws_cs', 'trial_number']
    all_events = s_task[1][ev_cols]
    return new_events, all_events
# taskfilesdir 
# outTask_dir = 

def main():
    get_new_events()
    
if __name__ == "__main__":
    main()
