#! /usr/bin/env python

import os
import pandas as pd
import shutil

import sniffbytes as snif

from os.path import basename as bname
from os.path import dirname as dname
from os.path import join as pjoin
from pandas import DataFrame as df
from tqdm import tqdm
from typing import Union
from zipfile import ZipFile

from sniffbytes import filter_lst_exc
from sniffbytes import filter_lst_inc

from sniffbytes import evenodd

from removeEmptyFolders import removeEmptyFolders

def getnametuple(myzip):
    """
    Adjustment to ZipFile.namelist() function to prevent MAC-exclusive
    '__MACOSX' and '.DS_Store' files from interfering.
    Only necessary for files compressed with OS 10.3 or earlier.
    Source: https://superuser.com/questions/104500/what-is-macosx-folder
    Command line solution:
        ``` zip -r dir.zip . -x ".*" -x "__MACOSX"
    Source: https://apple.stackexchange.com/questions/239578/compress-without-ds-store-and-macosx
    
    Parameters
    ----------
    myzip: ZipFile object
    """
    return tuple(
        sorted(
            list(
                itm
                for itm in myzip.namelist()
                if bname(itm).startswith(".") == False
                and "__MACOSX" not in itm
                and "textClipping" not in itm
                and itm != os.path.splitext(bname(dname(itm)))[0] + "/"
            )
        )
    )

def scanzip2(archv_path: Union[os.PathLike, str],
            ntpl: Union[str, list, tuple] = [],
            exclude: Union[str, list, tuple] = [],
            include: Union[str, list, tuple] = [],
            to_xtrct: Union[str, list, tuple] = [],
            dst_path: Union[str, os.PathLike] = None,
            to_sniff: bool = False) -> object:
    ''' Scans contents of ZipFile object as bytes
        Returns DataFrame containing typical ZipFile.ZipInfos
        objects informations along with a raw bytes buffer
        for future editing
        
        Parameters
        ----------
        archv_path: Path to zip file
        ntpl: Sequence of file names from the archive
                - See - help(getnametpl)
        exclude: Sequence of either names, extensions or
                 some pattern found in file names of files
                 to be excluded from 'scanzip' return value
    '''
    myzip = ZipFile(archv_path)
    dst_path = [dst_path if dst_path else
                pjoin(os.getcwd(),
                      os.path.splitext(bname(archv_path))[1])][0]
    os.makedirs(dst_path, exist_ok = True)

    ntpl = [ntpl if ntpl else snif.filter_lst_exc(exclude,
                                                  getnametuple(myzip))][0]
    vals = df(
            tuple(
                dict(zip(snif.evenodd(itm)[0], snif.evenodd(itm)[1]))
                for itm in tuple(
                    tuple(
                        snif.is_printable(repr(itm.lower()))
                        .strip()
                        .replace("'", "")
                        .replace("'", "")
                        .replace("=", " ")[:-2]
                        .split()
                    )[1:]
                    for itm in tqdm(set(
                        repr(myzip.getinfo(itm))
                        .strip(" ")
                        .replace(itm, itm.replace(" ", "_"))
                        if " " in itm
                        else repr(myzip.getinfo(itm)).strip(" ")
                        for itm in ntpl
                    ), desc = 'scanning archive')
                )
            )
        ).astype(object).sort_values("filename").reset_index(drop=True)
    vals['filename'] = [row[1].filename.replace("/", "_").replace("-", "_").lower()
                        for row in vals.iterrows()]
    vals['src_names'] = sorted(ntpl)
#     removeEmptyFolders(dst_path)   
    vals['bsheets'] = [myzip.open(row[1].src_names).read()
                           for row in vals.iterrows()]
    myzip.close()
    os.makedirs(dst_path, exist_ok = True)
    [snif.stream2file(row[1].bsheets, pjoin(dst_path, row[1].filename))
     for row in vals.iterrows() if row[1].filename in
     snif.filter_lst_inc(to_xtrct, vals.filename)]
    vals = vals.drop([row[0] for row in vals.iterrows() if row[1].filename in
                      snif.filter_lst_inc(to_xtrct, vals.filename)], axis = 0)
    
    if to_sniff:
        sniffed = df((snif.sniff_bytes(row[1].bsheets)
                     for row in vals.iterrows())).astype(object).to_dict()
        vals = df.from_dict({**vals.to_dict(), **sniffed},
                            orient = 'index').astype(object)
    return vals

def main():    
    if __name__ == "__main__":
        scanzip2(archv_path, ntpl, exclude, to_xtrct, dst_path)