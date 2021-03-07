#! /usr/bin/env python

import os
import pandas as pd

import sniffbytes as snif

from os.path import basename as bname
from os.path import dirname as dname
from pandas import DataFrame as df
from typing import Union
from zipfile import ZipFile

from sniffbytes import filter_lst_exc

def getnametuple(myzip):
    """
    Adjustment to ZipFile.namelist() function to prevent MAC-exclusive
    '__MACOSX' and '.DS_Store' files from interfering.
    Only necessary for files compressed with OS 10.3 or earlier.
    Source: https://superuser.com/questions/104500/what-is-macosx-folder
    Command line solution:
        ``` zip -r dir.zip . -x ".*" -x "__MACOSX"
    Source: https://apple.stackexchange.com/questions/239578/compress-without-ds-store-and-macosx
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

def get_zip_contents(
    archv_path: Union[os.PathLike, str],
    ntpl: Union[str, list, tuple] = [],
    exclude: Union[str, list, tuple] = [],
    to_xtrct: Union[str, list, tuple] = [],
    to_close: bool = True,
    withbytes: bool = False,
    to_sniff: bool = False
) -> object:
    myzip = ZipFile(archv_path)
    ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

    vals = (
        df(
            tuple(
                dict(zip(snif.evenodd(itm)[0], snif.evenodd(itm)[1]))
                for itm in tuple(
                    tuple(snif.no_ascii(repr(
                        itm.lower())).strip().replace("'", "")
                        .replace("'", "")
                        .replace("=", " ")[:-2]
                        .split()
                    )[1:]
                    for itm in set(
                        repr(myzip.getinfo(itm))
                        .strip(" ")
                        .replace(itm, itm.replace(" ", "_"))
                        if " " in itm
                        else repr(myzip.getinfo(itm)).strip(" ")
                        for itm in ntpl
                    )
                )
            ),
            dtype="object",
        )
        .sort_values("filename")
        .reset_index(drop=True)
    )
    vals[["src_name", "ext"]] = [(nm, os.path.splitext(nm)[1]) for nm in ntpl]
    vals["filename"] = [
        "_".join(
            pd.Series(
                row[1].filename.lower().replace("/",
                                                "_").replace("-",
                                                             "_").split("_")
            ).unique()
            .__iter__()
        )
        for row in vals.iterrows()
    ]
    if exclude:
        vals = vals.drop(
            [
                row[0]
                for row in vals.iterrows()
                if row[1].filename
                not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
            ],
            axis=0,
        )
    if withbytes:
        vals["bsheets"] = [
#             snif.strip_null() 
            myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
        ]
    if to_sniff:
        vals[["encoding", "delimiter", "has_header", "width", "dup_index", "nrows"]] = \
            [tuple(snif.scan_bytes(row[1].bsheets).values()) for row in vals.iterrows()]
    if to_close:
        myzip.close()
        return vals
    else:
        return (myzip, vals)
        
def main():    
    if __name__ == "__main__":
        repair_dataset(folderpath, dst_path, exclude)
