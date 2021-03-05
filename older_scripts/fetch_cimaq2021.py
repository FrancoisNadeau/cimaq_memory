#!/usr/bin/env python3

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

from loading_utils import megamerge
from loading_utils import loadmeansheets
from loading_utils import loadpaths
from loading_utils import makeindexes
from loading_utils import loadinfos2

cimaq = loadinfos2()
class participant():
    def __init__(self):
        self.infos = loadinfos2().sample().squeeze()
        self.name = self.infos.name
        self.t_r = nib.load(self.infos.func).header.get_zooms()[-1]
        self.confounds = pd.read_csv(self.infos.confounds, sep='\t')
        self.n_frames = self.confounds.shape[0]
        self.frame_times = np.arange(self.n_frames) * self.t_r
        self.events = pd.read_csv(self.infos.events2,
                                  sep='\t').drop('Unnamed: 0', axis=1)
        self.ctl = pd.read_csv(self.infos.ctlonly,
                                  sep='\t').drop('Unnamed: 0', axis=1)
        self.anat = nib.load(self.infos.anat)
        self.func = nib.load(self.infos.func)
        self.meandatas = flatten(df(self.infos.mean_datas.loc['infos'].squeeze(
        )).T.values[:int(self.name)][0])
        self.behav = df(pd.Series(flatten(tuple(zip(subject.meandatas))))[0])
        self.groups = df(pd.Series(flatten(tuple(zip(subject.meandatas))))[1])
        self.mean_motion = df(pd.Series(flatten(tuple(zip(subject.meandatas))))[2])        
        self.npsych = df(pd.Series(flatten(tuple(zip(subject.meandatas))))[3])
        self.matrix01 = self.matrix1()
        self.matrix02 = self.matrix2()
    def matrix1(self):
        return mfldm(frame_times=self.frame_times, events=self.events[self.events.Condition == 'Enc'], hrf_model='spm',
                            drift_model=None, high_pass=0.05,
                            add_regs=self.confounds)
    def matrix2(self):
        return mfldm(frame_times=self.frame_times, events=self.ctl, hrf_model='spm',
                     drift_model=None, high_pass=0.05)
subject = participant()
