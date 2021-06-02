#! /usr/bin/env python

import os
import pandas as pd
import zipfile

import sniffbytes as snif

from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join as pjoin
from pandas import DataFrame as df
from tqdm import tqdm
from typing import Union
from zipfile import ZipFile

from sniffbytes import filter_lst_exc
from sniffbytes import filter_lst_inc

from sniffbytes import evenodd
from sniffbytes import stream2file

def getnametuple(
    myzip: zipfile.ZipFile
) -> tuple:
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

def get_ntpl(
    myzip: zipfile.ZipFile,
    ntpl: Union[list, tuple] = None,
    exclude: Union[str, list, tuple] = None
) -> list:
    return [ntpl if ntpl else
            [snif.filter_lst_exc(exclude,
                                 getnametuple(myzip))
             if exclude else getnametuple(myzip)][0]][0]

def zscanner(
    myzip: Union[str, zipfile.ZipFile],
    ntpl: Union[list, tuple] = None,
    exclude: Union[str, list, tuple] = None
) -> pd.DataFrame:
    return df(tuple(dict((zip(snif.evenodd(itm)[0],
                              snif.evenodd(itm)[1])))
                    for itm in tuple(tuple(
                        snif.is_printable(repr(itm.lower()))
                        .strip()
                        .replace("'", "")
                        .replace("'", "")
                        .replace("=", " ")[:-2]
                        .split())[1:] for itm in tqdm(
                        set(repr(myzip.getinfo(itm)).strip(" ")
                            .replace(itm, itm.replace(" ", "_"))
                            if " " in itm
                            else repr(myzip.getinfo(itm)).strip(" ")
                            for itm in get_ntpl(myzip, ntpl, exclude)),
                        desc = "scanning archive"))),
              dtype = object).sort_values("filename").reset_index(drop=True)

def get_dst_path(
    archv_path: Union[os.PathLike, str],
    dst_path: Union[str, os.PathLike] = None
) -> os.PathLike:
    return [dst_path if dst_path
            else pjoin(os.getcwd(),
                       os.path.splitext(bname(archv_path))[1])][0]

def save_archv(
    vals: pd.DataFrame,
    to_xtrct: Union[str, list, tuple],
    dst_path: Union[str, os.PathLike]
) -> None:
    [stream2file(row[1].bsheets,
                 pjoin(get_dst_path(dst_path),
                       bname(row[1].filename).lower()))
     for row in vals.iterrows() if row[1].src_names in
     tqdm(filter_lst_inc(to_xtrct, vals.src_names),
          "extracting archive")]

def xtrct_archv(
    vals: pd.DataFrame,
    to_xtrct: Union[str, os.PathLike],
    dst_path: Union[str, os.PathLike]
) -> pd.DataFrame:
    return vals.loc[[row[0] for row in vals.iterrows()
                     if row[1].src_names not in
                     filter_lst_inc(to_xtrct, vals.src_names)]]

def scanzip(
    archv_path: Union[os.PathLike, str],
    ntpl: Union[str, list, tuple] = None,
    exclude: Union[str, list, tuple] = None,
    to_xtrct: Union[str, list, tuple] = None,
    dst_path: Union[str, os.PathLike] = None
) -> object:
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
    ntpl = get_ntpl(myzip, ntpl, exclude)
    vals = zscanner(myzip, ntpl)
    vals['filename'] = [row[1].filename.replace("/", "_")
                        for row in vals.iterrows()]
    vals['src_names'] = sorted(ntpl)
    vals['bsheets'] = [myzip.open(row[1].src_names).read().lower()
                       for row in tqdm(vals.iterrows(),
                                       desc = "reading archive")]
    myzip.close()    

    if to_xtrct:
        save_archv(vals, to_xtrct, dst_path)
        return xtrct_archv(vals, to_xtrct, dst_path)
    else:
        return vals

def main():    
    if __name__ == "__main__":
        scan_zip(archv_path, ntpl, exclude, to_xtrct, dst_path)

