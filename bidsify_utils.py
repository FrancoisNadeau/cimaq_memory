#!/usr/bin/env python3

import os
import pandas as pd
from pandas import DataFrame as df
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import join as pjoin

from typing import Union

def bidsify_names(name: str) -> str:
    ''' Pads a filename if run number or task name are missing '''    
    def get_runs(name:str)->str:
        return '_'.join([name.split('_') if 'run' in name
                         else name.split('_')[:2] + \
                                       ['run-01'] + name.split(
                             '_')[2:]][0])
    def get_tasks(name:str)->str:
        return '_'.join([name.split('_') if 'task' in name
                         else name.split('_')[:-1] + \
                                       ['task-idle'] + name.split(
                             '_')[3:]][0])
    return get_tasks(get_runs(name))


##################### Copied from sniffbytes.py ########################

def bidsify_lim(indir: Union[os.PathLike, str]) -> list:
    """ Description
        -----------
        Lists the full relative path of all '.jpeg' files in a directory.
        Only lists files, not directories.

        Parameters
        ----------
        imdir: type = str
            Name of the directory containing the images.

        Return
        ------
        imlist: type = list
        1D list containing all '.jpeg' files' full relative paths """
    imlist = []
    for allimages in os.walk(indir):
        for image in allimages[2]:
            indir = pjoin(allimages[0], image)
            if os.path.isfile(indir):
                imlist.append(indir)
    return imlist

def bidsify_df(
    pathlist: Union[list, tuple]
) -> object:
    return (df(((bidsify_names(bname(sheet).split(".", 1)[0]),
                "." + bname(sheet).split(".", 1)[1],
                 bname(dname(sheet)), sheet,)
                for sheet in pathlist),
                dtype = object,
                columns=["filename", "ext", "parent", "fpaths"],
        ).sort_values("filename").reset_index(drop=True))

###########################################################################


def bidsify_load_scans(
    maindir: Union[str, os.PathLike],
    id_list: Union[list, tuple, pd.Series,
                   pd.DataFrame, os.PathLike] = None,
) -> Union[object, pd.DataFrame]:
    ''' Returns a pd.DataFrame object containg dataset files
        sorted by columns named according to BIDS specifications.
        Practical for sorting and indexing files 
        - subid, ses, run, task and modality. '''
    
    def bidsify_sort(name: str) -> str:
        ''' Generates pd.Series object from a file's name according to BIDS. '''
        return pd.Series((bidsify_names(name).split('_')), 
                          index = ['subid', 'ses', 'run',
                                   'task', 'modality'],
                          name = name)
    
    subjects = pd.concat([bidsify_df(bidsify_lim(pjoin(maindir, itm)))
                      for itm in ls(maindir) if 'sub' in itm
                      and itm.split('-')[1] in
                      id_list], ignore_index = True).sort_values(
                              'filename').reset_index(drop = True)
    scaninfos = df((bidsify_sort(name)
                    for name in subjects.filename)).reset_index(drop = True)
    return pd.concat([subjects, scaninfos], axis = 1)


