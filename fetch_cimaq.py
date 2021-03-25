#! /usr/bin/env python

import os
import pandas as pd
import numpy as np
import shutil

from io import StringIO
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

def instantiate_cimaq(reset: bool = False) -> None:
    if reset:
        try:
            shutil.rmtree(pjoin(os.getcwd(), 'newtest'))
            [os.makedirs(pjoin(os.getcwd(), 'newtest', item), exist_ok = True)
             for item in  ['events', 'behavioural',
                           'cimaq_uzeprimes', 'nilearn_events']]            
        except FileNotFoundError:
            [os.makedirs(pjoin(os.getcwd(), 'newtest', item), exist_ok = True)
             for item in  ['events', 'behavioural',
                           'cimaq_uzeprimes', 'nilearn_events']]
    else:
        [os.makedirs(pjoin(os.getcwd(), 'newtest', item), exist_ok = True)
         for item in  ['events', 'behavioural',
                       'cimaq_uzeprimes', 'nilearn_events']]

def get_qc_list() -> list:
    return pd.read_csv(pjoin(os.getcwd(),
                             "sub_list_TaskQC.csv"),
                       header = None).astype(str).values.tolist()[0][1:]

def load_series_uid() -> pd.DataFrame:
    qcok = get_qc_list()
    return df((row[1] for row in tqdm(pd.read_csv(
        pjoin(os.getcwd(), "seriesUID_qc.csv")).iterrows(),
                                      desc = "loading")
              if str(row[1].CandID) in qcok))

def get_cimaq_ids() -> list:
    return df((itm.split("_") + [itm] for itm in
               pd.Series(("_".join((str(itm) for itm in
                                    row[1].values))
                          for row in
                          load_series_uid().iloc[:, :2].iterrows())).unique()),
              columns = ["pscid", "dccid", "subid"])

def load_subjects(src_dir: Union[str, os.PathLike]) -> list:
    return df(((sub.split("-")[1],
                loadimages(pjoin(xpu(src_dir), sub)))
                 for sub in tqdm(filter_lst_inc(get_qc_list() + ["sub"],
                                             ls(xpu(src_dir))),
                            desc = 'loading subject files')))

def get_cimaq_zeprime(cimaq_dir: Union[str, os.PathLike]) -> pd.DataFrame:
    return snif.loadfiles(snif.filter_lst_inc(get_qc_list(),
                                              snif.loadimages(xpu(pjoin(
                        cimaq_dir, 'derivatives/CIMAQ_fmri_memory/data',
                        'task_files/zipped_eprime')))))

def xtrct_cimaq(cimaq_dir: Union[str, os.PathLike]) -> pd.DataFrame:
    return pd.concat([scanzip(apath,
                            exclude = ['Practice', 'Pratique',
                                       'PRATIQUE', 'PRACTICE', 'READ',
                                       'Encoding-scan', 'Retrieval-'],
                            to_xtrct = ['.pdf', '.edat2'],
                            dst_path = pjoin(os.getcwd(), 'newdevs',
                                             'cimaq_uzeprimes'))
                    for apath in
                      tqdm(get_cimaq_zeprime(cimaq_dir).fpaths,
                           desc = 'scanning archive')],
                     ignore_index = True).sort_values('filename').reset_index(drop = True)

def index_cimaq(vals: pd.DataFrame,
                cimaq_dir: Union[str, os.PathLike]) -> pd.DataFrame:
    vals[['has_header', 'subid']] = \
        [[snif.get_has_header(row[1].bsheets)] + \
         ['_'.join(row[1].src_names.replace('-', '_').split('_')[:2])]
         for row in tqdm(vals.iterrows(), desc = 'indexing participants')]
    return vals

def clean_cimaq(vals: pd.DataFrame) -> pd.DataFrame:
    vals['clean_sheets'] = [pd.read_csv(StringIO(snif.clean_bytes(row[1].bsheets
                                                                 ).decode()),
                                        header = [0 if row[1].has_header else None][0],
                                        sep = '\t', dtype = object)
                            for row in tqdm(vals.iterrows(),
                                            desc = 'cleaning')]
    return vals

def group_cimaq(vals: pd.DataFrame) -> np.flatiter:
    return df.from_dict((dict((grp, vals.groupby('subid').get_group(
               grp).sort_values('filename').reset_index(drop = True))
                              for grp in tqdm(vals.groupby('subid').groups,
                                              desc = 'grouping participants'))),
                        orient = 'index').values.flat

def load_cimaq(cimaq_dir: Union[str, os.PathLike]) -> np.flatiter:
    instantiate_cimaq(reset = True)
    valus = group_cimaq(clean_cimaq(index_cimaq(xtrct_cimaq(cimaq_dir), cimaq_dir)))
    return df((((vals.iloc[0].subid,
                 pjoin(os.getcwd(), 'newtest', 'events', 'sub-_' + \
                                 vals.iloc[0].subid + \
                                 '_run-01_task-encoding_events.tsv'),
                       pd.concat([vals.iloc[1].clean_sheets,
                                  vals.iloc[0].clean_sheets.loc[:, 5:8]],
                                 axis = 1).drop(6, axis = 1).rename(
                           columns = {5: 'onset', 7: 'fix_onset', 8: 'fix_duration'}).to_csv(
                           pjoin(os.getcwd(), 'newtest', 'events', 'sub-_' + \
                                 vals.iloc[0].subid + \
                                 '_run-01_task-encoding_events.tsv'))).__iter__(),
                 (pjoin(
                           os.getcwd(), 'newtest', 'behavioural', 'sub-_' + \
                           vals.iloc[2].subid + \
                           '_run-01_task-encoding_behavioural.tsv'),
                       vals.iloc[2].clean_sheets.to_csv(pjoin(
                           os.getcwd(), 'newtest', 'behavioural', 'sub-_' + \
                           vals.iloc[2].subid + \
                           '_run-01_task-encoding_behavioural.tsv'))))
                for vals in tqdm(valus,
                                 desc = 'fetching CIMAQ'))).values.flat

def load_cimaq_scans(cimaq_dir: Union[str, os.PathLike]) -> np.flatiter:
    scan_infos = bidsify_load_scans(cimaq_dir, get_qc_list())
    scan_infos['dccid'] = sorted([(filename, filename.split('-')[1].split('_')[0])[1]
                                  for filename in scan_infos.filename])
    scan_infos = df(((grp, scan_infos.groupby('dccid').get_group(grp))
                     for grp in tqdm(scan_infos.groupby('dccid').groups,
                                     desc = 'loading subjects'))).set_index(
                        0).sort_index().reset_index(drop = False)
    scan_infos['subid'] = [[itm for itm in get_qc_list() if
                           itm in str(row[0])] for row in scan_infos.iterrows()]
    return scan_infos.set_index('subid', drop = True).values.flat


def get_cimaq_confounds(cimaq_dir: Union[str, os.PathLike]) -> np.flatiter:
    return df((apath for apath in
                           tqdm(snif.filter_lst_inc(get_qc_list(),
                                    snif.loadimages(pjoin(cimaq_dir,
                              'derivatives/CIMAQ_fmri_memory/data',
                                  'confounds', 'resample'))),
               desc = 'loading confounds'))).values.flat

def fetch_cimaq(cimaq_dir: Union[str, os.PathLike]) -> pd.DataFrame:
    return pd.concat([df(load_cimaq(cimaq_dir).base),
                      df(get_cimaq_confounds(cimaq_dir).base),
                      df(load_cimaq_scans(cimaq_dir).base)],
                     axis = 1).T.reset_index(drop = True).T.rename(columns = {0: 'subid', 1: 'events',
                                                 2: 'behav', 3:'confounds',
                                                 4: 'dccid', 5: 'scans'})
def main():    
    if __name__ == "__main__":
        return fetch_cimaq(cimaq_dir)

# def load_cimaq(cimaq_dir: Union[str, os.PathLike]) -> np.flatiter:
#     instantiate_cimaq(reset = True)
#     valus = group_cimaq(clean_cimaq(index_cimaq(xtrct_cimaq(cimaq_dir), cimaq_dir)))
#     return df((((vals.iloc[0].subid,
#                  next((pd.concat([vals.iloc[1].clean_sheets.rename(
#                      columns = {'category': 'trial_type'}),
#                                   vals.iloc[0].clean_sheets.loc[:, 5:8],
#                                  pd.Series(vals.iloc[0].clean_sheets[8].astype(float) + 3.0,
#                                            name = 'duration').round(0)],
#                         axis = 1).drop(6, axis = 1).rename(
#                             columns = {5: 'onset', 7: 'fix_onset', 8: 'fix_duration'}),
#                        pd.concat([vals.iloc[1].clean_sheets,
#                                   vals.iloc[0].clean_sheets.loc[:, 5:8]],
#                                  axis = 1).drop(6, axis = 1).rename(
#                            columns = {5: 'onset', 7: 'fix_onset', 8: 'fix_duration'}).to_csv(
#                            pjoin(os.getcwd(), 'newtest', 'events', 'sub-_' + \
#                                  vals.iloc[0].subid + \
# #                                  vals.iloc[0].dccid + '_' + vals.iloc[0].pscid + \
#                                  '_run-01_task-encoding_events.tsv'))).__iter__()),
#                  next((vals.iloc[2].clean_sheets,
#                        vals.iloc[2].clean_sheets.to_csv(pjoin(
#                            os.getcwd(), 'newtest', 'behavioural', 'sub-_' + \
#                            vals.iloc[2].subid + \
# #                            vals.iloc[2].dccid + '_' + vals.iloc[2].pscid + \
#                            '_run-01_task-encoding_behavioural.tsv'))).__iter__())).__iter__()
#                 for vals in tqdm(valus,
#                                  desc = 'fetching CIMAQ')))).values.flat


# def load_cimaq(cimaq_dir: Union[str, os.PathLike]) -> np.flatiter:
#     instantiate_cimaq(reset = True)
#     valus = group_cimaq(clean_cimaq(index_cimaq(xtrct_cimaq(cimaq_dir), cimaq_dir)))
#     return df((((vals.iloc[0].subid,
#                  pjoin(os.getcwd(), 'newtest', 'events', 'sub-_' + \
#                                  vals.iloc[0].subid + \
#                                  '_run-01_task-encoding_events.tsv'),
#                  pd.concat([vals.iloc[1].clean_sheets,
#                                   vals.iloc[0].clean_sheets.loc[:, 5:8]],
#                                  axis = 1).drop(6, axis = 1).rename(
#                            columns = {5: 'onset', 7: 'fix_onset', 8: 'fix_duration'}).to_csv(
#                            pjoin(os.getcwd(), 'newtest', 'events', 'sub-_' + \
#                                  vals.iloc[0].subid + \
#                                  '_run-01_task-encoding_events.tsv')),
#                  pjoin(os.getcwd(), 'newtest', 'behavioural', 'sub-_' + \
#                        vals.iloc[2].subid + \
#                            '_run-01_task-encoding_behavioural.tsv'),
#                        vals.iloc[2].clean_sheets.to_csv(pjoin(
#                            os.getcwd(), 'newtest', 'behavioural', 'sub-_' + \
#                            vals.iloc[2].subid + \
#                            '_run-01_task-encoding_behavioural.tsv')))
#                 for vals in tqdm(valus,
#                                  desc = 'fetching CIMAQ')))).values.flat


# def index_cimaq(vals: pd.DataFrame,
#                 cimaq_dir: Union[str, os.PathLike]) -> pd.DataFrame:
#     vals[['has_header', 'subid']] = \
#          [(snif.get_has_header(row[1].bsheets),
#            snif.filter_lst_inc([str(row[1].filename.split('_')[0].split('-')[1])],
#                                 get_cimaq_ids(cimaq_dir)))
#           for row in tqdm(
#               vals.iterrows(),
#               desc = 'indexing participants')]
#     return vals
