#!/usr/bin/python3

''' Creates a .tar.xz archive of CIMA-Q dataset MRI & fMRI scans '''

import os
import shutil
import tarfile
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join as pjoin
from typing import Union
import pandas as pd
from tqdm import tqdm
from fetch_cimaq import load_cimaq_scans
import sniffbytes as snif

def get_cimaq_qc(cimaq_dir: Union[str, os.PathLike]) -> list:
    ''' Return list of participant IDs who passed QC assertion '''
    return snif.clean_bytes(
        xpu(pjoin(cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
                  'participants/sub_list_TaskQC.tsv'))).decode().split()[1:]

def get_dst_path(
        dst_path: Union[str, os.PathLike] = None
        ) -> Union[str, os.PathLike]:
    ''' Returns s default path for writing new archive if none is provided '''
    return [dst_path if dst_path else
            pjoin(dname(os.getcwd()), '_new_archive_' + \
            bname(os.getcwd()))][0]

def cpfiles(fpaths: Union[list, tuple, str],
            dst_path: Union[str, os.PathLike] = None) -> None:
    ''' Copies files from cimaq_dataset to local directory '''
    dst_path = get_dst_path(dst_path)
    return [shutil.copyfile(itm, os.path.join(dst_path, bname(itm)))
            for itm in tqdm([itm for itm in fpaths
                             if '.nii' in itm], desc ='copying files')]

def get_fpaths(fpaths: Union[list, tuple, str, os.PathLike]) -> list:
    ''' Returns either fpaths if it's a list of paths or
        recursively lists all files in a directory if
        fpaths points to a directory '''
    return sorted([snif.loadimages(fpaths) if
                   os.path.isdir(fpaths) else fpaths][0])
def to_txz(
        fpaths: Union[list, tuple, str, os.PathLike],
        dst_path: Union[str, os.PathLike] = None
        ) -> None:
    ''' Takes either a list of file paths or a directory path
        as inout and create a ".tar.xz" compressed archive with the input '''
    dst_path = get_dst_path(dst_path)
    fpaths = get_fpaths(fpaths)
    with tarfile.open(dst_path + '.tar.xz', 'w|xz') as newtar:
        for name in tqdm(fpaths, desc = 'compressing'):
            newtar.add(name)
    newtar.close()

def get_scan_archive(
    cimaq_dir: Union[str, os.PathLike],
    dst_path: Union[str, os.PathLike] = None
) -> None:
    ''' Completes the step from cpfiles '''
    dst_path = get_dst_path(dst_path)
    os.makedirs(dst_path, exist_ok = True)
    allscans_paths_uncomp = snif.filter_lst_inc(['.nii'], snif.filter_lst_exc(
    ['.gz'], pd.concat(list(itm.fpaths for itm in load_cimaq_scans(
        xpu(cimaq_dir)).scans.values.flat)).values.tolist()))
    fpaths = [itm for itm in snif.loadfiles(snif.filter_lst_inc(
        get_cimaq_qc(xpu(cimaq_dir)),
        allscans_paths_uncomp)).fpaths.values.tolist()
                if '.gz' not in itm]
    to_txz(fpaths, dst_path)

def main():
    ''' Runs get_scan_archive.py when called in command line '''
    if __name__ == "__main__":
        get_scan_archive(cimaq_dir='~/projects/rrg-pbellec/fnadeau/cimaq_03-19/cimaq_03-19',
                 dst_path='~/cimaq_2021_nifti_img_files''~/cimaq_2021_nifti_img_files')

get_scan_archive(cimaq_dir='~/projects/rrg-pbellec/fnadeau/cimaq_03-19/cimaq_03-19',
                 dst_path='~/cimaq_2021_nifti_img_files')
