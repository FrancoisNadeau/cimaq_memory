#! /usr/bin/env python

import os
import pandas as pd
import shutil
from pandas import DataFrame as df
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from typing import Union
from cimaq import cimaq

import sniffbytes as snif

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

def copy_cimaq(cimaq_dir: Union[str, os.PathLike]) -> None:
    testpaths = pd.concat([itm for itm in cimaq.scans.values.tolist()],
                          ignore_index = True).fpaths.values.tolist()
    os.makedirs(pjoin(os.getcwd(), 'cimaq_2021_test'), exist_ok = True)
    newpaths = [pjoin(os.getcwd(), 'cimaq_2021_test',
                      bname(bidsify_names(aname)))
                for aname in testpaths]
    [snif.stream2file(itm[0], itm[1]) for itm in tuple(zip(testpaths, newpaths))]

def main():    
    if __name__ == "__main__":
        copy_cimaq(cimaq_dir, dst_path)

# def copy_cimaq(cimaq_dir: Union[str, os.PathLike],
#                dst_path: Union[str, os.PathLike] = None) -> None:
#     dst_path = [dst_path if dst_path
#                               else pjoin(dname(os.getcwd()),
#                                          'cimaq_2021_test')][0]
#     os.makedirs(dst_path, exist_ok = True)
#     [snif.stream2file(snif.get_bytes(itm[0]), itm[1]) for itm in
#             tqdm(tuple(zip([pjoin(dst_path,
#                   bname(bidsify_names(aname)))
#             for aname in pd.concat([itm for itm in cimaq.fetch(cimaq_dir).scans.values.tolist()],
#                       ignore_index = True).fpaths.values.tolist()])),
#                  desc = 'copying CIMA-Q')]

