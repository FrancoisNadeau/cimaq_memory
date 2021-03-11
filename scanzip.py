#! /usr/bin/env python

import os
import pandas as pd

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

def scanzip(archv_path: Union[os.PathLike, str],
            ntpl: Union[str, list, tuple] = [],
            exclude: Union[str, list, tuple] = [],
            to_xtrct: Union[str, list, tuple] = [],
            dst_path: Union[str, os.PathLike] = None) -> object:
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
    [myzip.extract(nm, pjoin(dst_path, nm.lower().replace(' ', '_').strip()))
     for nm in snif.filter_lst_inc(to_xtrct, getnametuple(myzip))]
    ntpl = [ntpl if ntpl else snif.filter_lst_exc(
               exclude + snif.filter_lst_inc(to_xtrct, getnametuple(myzip)),
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
            ),
            dtype = object,
        ).sort_values("filename").reset_index(drop=True)

    vals['src_names'] = sorted(ntpl)
    vals['bsheets'] = [myzip.open(row[1].src_names).read()
                       for row in vals.iterrows()]
    
    myzip.close()
    sniffed = df((snif.scan_bytes(row[1].bsheets)
                 for row in vals.iterrows()), dtype = object).to_dict()
    return df.from_dict({**vals.to_dict(), **sniffed},
                        orient = 'index', dtype = object)

def main():    
    if __name__ == "__main__":
        scan_zip(archv_path, ntpl, exclude, to_xtrct, dst_path)

        
# def scansniff_zip(
#     archv_path: Union[str, os.PathLike],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     to_xtrct: Union[str, list, tuple] = [],
#     dst_path: Union[str, os.PathLike] = None
# ) -> object:
#     scanned_zip = [scanzip(fpath, ntpl,to_xtrct=[], exclude,
#                            to_xtrct, dst_path, withbytes=True)
#                    for fpath in tqdm(filter_lst_exc(
#                        exclude, sorted(snif.loadimages(archv_path))),
#                                      desc="scanning")]
#     zip_contents = [df(pd.concat([row[1], pd.Series(snif.scan_bytes(row[1]["bsheets"]),
#                                                     dtype = object)])
#                        for row in itm.sort_values("filename").iterrows())
#                     for itm in tqdm(scanned_zip, desc="sniffing")]
#     return zip_contents

# def get_zip_contents(
#     archv_path: Union[os.PathLike, str],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     to_xtrct: Union[str, list, tuple] = [],
#     to_close: bool = True,
#     withbytes: bool = False,
#     to_sniff: bool = False
# ) -> object:
#     myzip = ZipFile(archv_path)
#     ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

#     vals = (
#         df(
#             tuple(
#                 dict(zip(snif.evenodd(itm)[0], snif.evenodd(itm)[1]))
#                 for itm in tuple(
#                     tuple(snif.force_ascii(repr(
#                         itm.lower())).strip().replace("'", "")
#                         .replace("'", "")
#                         .replace("=", " ")[:-2]
#                         .split()
#                     )[1:]
#                     for itm in set(
#                         repr(myzip.getinfo(itm))
#                         .strip(" ")
#                         .replace(itm, itm.replace(" ", "_"))
#                         if " " in itm
#                         else repr(myzip.getinfo(itm)).strip(" ")
#                         for itm in ntpl
#                     )
#                 )
#             ),
#             dtype="object",
#         )
#         .sort_values("filename")
#         .reset_index(drop=True)
#     )
#     vals[["src_name", "ext"]] = [(nm, os.path.splitext(nm)[1]) for nm in ntpl]
#     vals["filename"] = [
#         "_".join(
#             pd.Series(
#                 row[1].filename.lower().replace("/",
#                                                 "_").replace("-",
#                                                              "_").split("_")
#             ).unique()
#             .__iter__()
#         )
#         for row in vals.iterrows()
#     ]
#     if exclude:
#         vals = vals.drop(
#             [row[0] for row in vals.iterrows() if row[1].filename
#              not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
#             ],
#             axis=0,
#         )
#     if withbytes:
#         vals["bsheets"] = [
# #             snif.strip_null() 
#             myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
#         ]
#     if to_sniff:
#         vals[["encoding", "delimiter", "has_header", "width", "dup_index", "nrows"]] = \
#             [tuple(snif.scan_bytes(row[1].bsheets).values()) for row in vals.iterrows()]
#     if to_close:
#         myzip.close()
#         return vals
#     else:
#         return (myzip, vals)

# def get_zip_contents(
#     archv_path: Union[os.PathLike, str],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     withbytes: bool = False,
#     to_sniff: bool = False,
#     to_close: bool = True,
# ) -> object:
#     myzip = ZipFile(archv_path)
#     ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

#     vals = (
#         df(
#             tuple(
#                 dict(zip(evenodd(itm)[0], evenodd(itm)[1]))
#                 for itm in tuple(
#                     tuple(
#                         force_ascii(repr(itm.lower()))
#                         .strip()
#                         .replace("'", "")
#                         .replace("'", "")
#                         .replace("=", " ")[:-2]
#                         .split()
#                     )[1:]
#                     for itm in set(
#                         repr(myzip.getinfo(itm))
#                         .strip(" ")
#                         .replace(itm, itm.replace(" ", "_"))
#                         if " " in itm
#                         else repr(myzip.getinfo(itm)).strip(" ")
#                         for itm in ntpl
#                     )
#                 )
#             ),
#             dtype="object",
#         )
#         .sort_values("filename")
#         .reset_index(drop=True)
#     )
#     vals[["src_name", "ext"]] = [(nm, os.path.splitext(nm)[1]) for nm in ntpl]
#     vals["filename"] = [
#         "_".join(
#             pd.Series(
#                 row[1].filename.lower().replace("/",
#                                                 "_").replace("-",
#                                                              "_").split("_")
#             ).unique()
#             .__iter__()
#         )
#         for row in vals.iterrows()
#     ]
#     if exclude:
#         vals = vals.drop(
#             [
#                 row[0]
#                 for row in vals.iterrows()
#                 if row[1].filename
#                 not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
#             ],
#             axis=0,
#         )

#     if withbytes:
#         vals["bsheets"] = [
# #             snif.strip_null() 
#             myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
#         ]
        
#     if to_sniff:
#         vals[["encoding", "delimiter", "has_header", "width", "dup_index", "nrows"]] = \
#             [tuple(snif.scan_bytes(row[1].bsheets).values()) for row in vals.iterrows()]
#     if to_close:
#         myzip.close()
#         return vals
#     else:
#         return (myzip, vals)
        

