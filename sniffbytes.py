#!/usr/bin/env python3

import chardet
import itertools
import gzip
import itertools
import json
import lzma
import numpy as np
import os
import pandas as pd
import regex as re
import reprlib
import string
import shutil
import sys
import tarfile
import zipfile

from chardet import UniversalDetector as udet
from collections import Counter
from functools import reduce
from io import StringIO
from numpy import nan as NaN
from operator import itemgetter
from os import listdir as ls
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join as pjoin
from os.path import splitext
from pandas import DataFrame as df
from tqdm import tqdm
from typing import Sequence
from typing import Union
from unidecode import unidecode
from zipfile import ZipFile

from removeEmptyFolders import removeEmptyFolders

def loadimages(indir: Union[os.PathLike, str]) -> list:
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

def flatten(nested_seq) -> list:
    """ Description
        -----------
        Returns unidimensional list from nested list using list comprehension.
        ----------
        Parameters
        ----------
            nestedlst: list containing other lists etc.
        ---------
        Variables
        ---------
            bottomElem: type = str
            sublist: type = list
        ------
        Return
        ------
        flatlst: unidimensional list 
    """
    return [bottomElem for sublist in nested_seq
               for bottomElem in (flatten(sublist) if
               (isinstance(sublist, Sequence) and not isinstance(sublist, str))
            else [sublist])]

def loadfiles(pathlist: Union[list, tuple]) -> object:
    return (df(((bname(sheet).split(".", 1)[0],
                "." + bname(sheet).split(".", 1)[1], sheet,)
                for sheet in pathlist),
                columns=["fname", "ext", "fpaths"],
        ).sort_values("fname").reset_index(drop=True))

def sortmap(info_df: object, patterns: object) -> object:
    """Identifies files in info_df with boolean values
    True: Pattern is in filename; False: It is not"""
    patterns = df(patterns, columns=["ids", "patterns"])
    for row in patterns.iterrows():
        cmplr = re.compile(row[1]["patterns"])
        info_df[row[1]["ids"]] = [
            cmplr.search(row[1]["patterns"]).group() in fname for fname in info_df.fname
        ]
    return info_df


def find_key(input_dict: dict, value):
    """ Source: https://stackoverflow.com/questions/16588328/return-key-by-value-in-dictionary """
    return next((k for k, v in input_dict.items() if v == value), None)


def megamerge(dflist: list, howto: str, onto: str = None) -> object:
    return reduce(
        lambda x, y: pd.merge(x, y, on=onto, how=howto).astype("object"), dflist
    )


def get_bytes(inpt: Union[bytes, str, os.PathLike]) -> bytes:
    """ Returns bytes from file either from memory or from reading """
    if os.path.isfile(inpt):
        with open(inpt, "rb", buffering=0) as myfile:
            outpt = myfile.read()
            myfile.close()
    if type(inpt) == bytes:
        outpt = inpt
    return [outpt if bool(len(outpt.splitlines()) > 0 and outpt != None) else b"0"][0]


def get_bzip_enc(inpt: Union[bytes, str, os.PathLike]) -> str:
    inpt = get_bytes(inpt)
    detector = udet()
    detector.reset()
    while True:
        next((detector.feed(line) for line in inpt.splitlines()))
        if (
            not detector.done
            and not detector.result
            and detector.result["encoding"] != None
        ):
            continue
        else:
            break
        break
    detector.close()
    return detector.result["encoding"]


def get_has_header(inpt: Union[bytes, str, os.PathLike], encoding=None) -> bool:
    """ Returns True if 1st line of inpt is a header line """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return [
        bool(inpt[0] not in bytes(".-0123456789", encoding)) if len(inpt) > 1 else False
    ][0]


def get_widths(
    inpt: Union[bytes, str, os.PathLike], encoding: str = None, hdr: bool = None
) -> Union[str, int]:
    inpt = get_bytes(inpt).replace("\x00".encode(encoding), "".encode(encoding))
    lines = [inpt.splitlines()[1:] if hdr else inpt.splitlines()][0]
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return pd.Series(len(line) for line in lines).fillna(1).max()


def get_all_bitems(inpt: Union[bytes, str, os.PathLike], encoding: str = None):
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return [
        line.replace(bytes("\x00", encoding), bytes("n\a", encoding)).split()
        for line in bytes("\n", encoding)
        .join(inpt.splitlines())
        .split(bytes("\n", encoding))
    ]


def get_lineterminator(inpt: Union[bytes, str, os.PathLike]) -> bytes:
    inpt = get_bytes(inpt)
    return pd.Series(
        next(
            (
                itm[0].strip(itm[1])
                for itm in tuple(zip(inpt.splitlines(keepends=True), inpt.splitlines()))
            )
        )
    ).unique()[0]


def get_delimiter(inpt: Union[bytes, str, os.PathLike], encoding: str = None) -> bytes:
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return Counter(
        pd.Series(
            pd.Series(
                pd.Series(
                    next(
                        (
                            re.sub(
                                bytes("|", encoding).join(map(re.escape, itm[1])),
                                bytes("|", encoding),
                                itm[0],
                            )
                            for itm in tuple(
                                zip(
                                    inpt.splitlines(),
                                    [
                                        line.replace(
                                            bytes("\x00", encoding), bytes("", encoding)
                                        ).split()
                                        for line in bytes("\n", encoding)
                                        .join(inpt.splitlines())
                                        .split(bytes("\n", encoding))
                                    ],
                                )
                            )
                        )
                    )
                )
                .unique()
                .max()
                .split(bytes("\\", encoding))
            )
            .unique()[0]
            .split(bytes("|", encoding))[1:],
            dtype="object",
        ).unique()
    ).most_common(1)[0][0]


def get_dupindex(
    inpt: Union[bytes, str, os.PathLike], hdr: bool = False, delimiter: bytes = None
) -> bool:
    inpt = get_bytes(inpt)
    bytelines = [inpt.splitlines() if not hdr else inpt.splitlines()[1:]][0]
    ev_itms, od_itms = evenodd([line.split(delimiter) for line in bytelines])
    return bool([line[0] for line in ev_itms] == [line[0] for line in od_itms])


def get_dupvalues(
    inpt: Union[bytes, str, os.PathLike],
    encoding: str = None,
    hdr: bool = None,
    delimiter: bytes = None,
) -> list:
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    hdr = [hdr if hdr != None else get_has_header(inpt, encoding)][0]
    bytelines = [inpt.splitlines() if not hdr else inpt.splitlines()[1:]][0]
    ev_itms, od_itms = evenodd([line.split(delimiter) for line in bytelines])
    checkup = tuple(zip(list(df(ev_itms).iteritems()), list(df(od_itms).iteritems())))
    return [itm[0][1].all() == itm[1][1].all() for itm in checkup]


def scan_bytes(
    inpt: Union[bytes, str, os.PathLike], encoding: str = None, hdr: bool = None
) -> dict:
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    #     hdr = get_has_header(inpt, encoding)
    hdr = [hdr if hdr != None else get_has_header(inpt, encoding)][0]
    try:
        return dict(
            zip(
                ("encoding", "delimiter", "has_header", "width", "dup_index", "nrows"),
                (
                    encoding,
                    get_delimiter(inpt, encoding),
                    hdr,
                    get_widths(inpt, encoding, hdr),
                    get_dupindex(inpt),
                    len(inpt.splitlines()),
                ),
            )
        )
    except IndexError:
        return dict(
            zip(
                ("encoding", "delimiter", "has_header", "width", "dup_index", "nrows"),
                (["empty_datas"]) * 6,
            )
        )


def force_utf8(inpt: Union[bytes, str, os.PathLike], encoding: str = None) -> bytes:
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return (
        inpt.replace("0xff".encode(encoding), "".encode(encoding))
        .replace("\x00".encode(encoding), "".encode(encoding))
        .decode("ascii", "replace")
        .replace("�", "")
        .strip()
        .encode("utf8")
    )


def mkfrombytes(
    inpt: Union[bytes, str, os.PathLike],
    encoding: str = None,
    delimiter: bytes = None,
    hdr: bool = False,
    dupindex: bool = None,
    new_sep: bytes = b"\t",
) -> bytes:
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    delimiter = [delimiter if delimiter else get_delimiter(inpt)][0]

    return (
        b"\n".join(
            [
                re.sub(
                    b"\s{2,}",
                    new_sep,
                    re.sub(
                        delimiter,
                        new_sep,
                        re.sub(
                            delimiter + b"{2,}", delimiter + b"NaN" + delimiter, line
                        ),
                    ),
                )
                .strip()
                .replace(b" ", b"_")
                .replace(b"\x00", b"NaN")
                for line in force_utf8(inpt, encoding).splitlines()
            ]
        )
        .replace(delimiter, new_sep)
        .decode()
        .encode()
    )


def fix_dupindex(
    inpt: Union[bytes, str, os.PathLike],
    encoding: str = None,
    hdr: bool = False,
    delimiter: bytes = None,
) -> bytes:
    tmp = evenodd(force_utf8(mkfrombytes(get_bytes(inpt))).splitlines())

    evdf = df([line.decode().split() for line in tmp[0]])
    oddf = df([line.decode().split() for line in tmp[1]])

    booltest = [
        col for col in evdf.columns if evdf[col].values.all() == oddf[col].values.all()
    ]
    newsheet = pd.merge(evdf, oddf, on=booltest)
    return "\n".join(
        [
            "\t".join([itm for itm in line])
            for line in newsheet.rename(
                dict(enumerate(newsheet.columns))
            ).values.tolist()
        ]
    ).encode()


def scansniff(folderpath: Union[str, os.PathLike]) -> object:
    contents = loadfiles(sorted(loadimages(folderpath))).sort_values("fname")
    contents[["encoding", "delimiter", "has_header", "width", "dup_index", "nrows"]] = [
        pd.Series(scan_bytes(fpath)) for fpath in tqdm(contents.fpaths, desc="sniffing")
    ]
    return contents


def stream2file(inpt: Union[str, bytes], dst_path: Union[str, os.PathLike]) -> None:
    os.makedirs(dname(dst_path), exist_ok=True)
    with open(dst_path, "wb") as binary_file:
        binary_file.write(inpt)
        binary_file.close()


######### String Manipulation ########################################


def make_labels(datas: Union[dict, object], var_name: Union[int, str]) -> dict:
    """Returns dict of (key, val) pairs using 'enumerate' on possible values
    filtered by 'Counter' - can be used to map DataFrame objects -"""
    return dict(enumerate(Counter(datas[var_name]).keys(), start=1))


def no_ascii(astring: str) -> str:
    """
    Source: https://stackoverflow.com/questions/8689795/how-can-i-remove-non-ascii-characters-but-leave-periods-and-spaces-using-python
    """
    return "".join(filter(lambda x: x in set(string.printable), astring))


def letters(astring: str) -> str:
    """
    Source: https://stackoverflow.com/questions/12400272/how-do-you-filter-a-string-to-only-contain-letters
    """
    return "".join([ch for ch in astring if character.isalpha()])


def num_only(astring: str) -> str:
    return "".join(c for c in astring if c.isdigit())


def evenodd(inpt) -> tuple:
    """
    Source: https://www.geeksforgeeks.org/python-split-even-odd-elements-two-different-lists
    Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index

    """
    eveseq = tuple(ele[1] for ele in enumerate(inpt) if ele[0] % 2 == 0)
    oddseq = tuple(ele[1] for ele in enumerate(inpt) if ele[0] % 2 != 0)
    return (eveseq, oddseq)


def filter_lst_exc(
    exclude: Union[list, tuple], str_lst: Union[list, tuple], sort: bool = False
) -> list:
    """ https://www.geeksforgeeks.org/python-filter-list-of-strings-based-on-the-substring-list/ """
    outlst = [itm for itm in str_lst if all(sub not in itm for sub in exclude)]
    return [sorted(outlst) if sort else outlst][0]


def filter_lst_inc(
    inclst: Union[list, tuple], str_lst: Union[list, tuple], sort: bool = False
) -> list:
    """ https://www.geeksforgeeks.org/python-filter-list-of-strings-based-on-the-substring-list/ """
    outlst = [itm for itm in str_lst if any(sub in itm for sub in inclst)]
    return [sorted(outlst) if sort else outlst][0]


######## For ZipFile archives ########################################


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
    to_close: bool = True,
) -> object:
    myzip = ZipFile(archv_path)
    ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

    vals = (
        df(
            tuple(
                dict(zip(evenodd(itm)[0], evenodd(itm)[1]))
                for itm in tuple(
                    tuple(
                        no_ascii(repr(itm.lower()))
                        .strip()
                        .replace("'", "")
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
                row[1].filename.replace("/", "_").replace("-", "_").lower().split("_")
            )
            .unique()
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
    if to_close:
        myzip.close()
        return vals
    else:
        return (myzip, vals)


def scan_zip_contents(
    archv_path: Union[os.PathLike, str],
    ntpl: Union[str, list, tuple] = [],
    to_xtrct: Union[str, list, tuple] = [],
    exclude: Union[str, list, tuple] = [],
    to_close: bool = True,
    withbytes: bool = False,
    dst_path: Union[os.PathLike, str] = None,
) -> object:

    myzip, vals = get_zip_contents(archv_path, ntpl, exclude, to_close=False)
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
    if to_xtrct:
        dst_path = [
            dst_path
            if dst_path
            else pjoin(dname(archv_path), os.path.splitext(bname(archv_path))[0])
        ][0]
        os.makedirs(dst_path, exist_ok=True)
        xtrct_lst = vals.loc[
            [
                row[0]
                for row in vals.iterrows()
                if row[1].filename
                in filter_lst_inc(to_xtrct, list(vals.filename), sort=True)
            ]
        ]
        [
            shutil.move(
                myzip.extract(member=row[1].src_name, path=dst_path),
                pjoin(
                    dst_path,
                    "_".join(
                        pd.Series(
                            row[1].filename.lower().replace("-", "_").split("_")
                        ).unique()
                    ),
                ),
            )
            for row in tqdm(xtrct_lst.iterrows(), desc="extracting")
        ]
        vals = vals.loc[
            [
                row[0]
                for row in vals.iterrows()
                if row[1].filename not in xtrct_lst.values
            ]
        ]
        removeEmptyFolders(dst_path, False)
    if withbytes:
        vals["bsheets"] = [
            myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
        ]
    if to_close:
        myzip.close()
    return vals.reset_index(drop=True)


def scansniff_zip(
    folderpath: Union[str, os.PathLike], exclude: Union[str, list, tuple] = []
) -> object:
    scanned_zip = [
        scan_zip_contents(fpath, to_xtrct=[], exclude=exclude, withbytes=True)
        for fpath in tqdm(
            filter_lst_exc(exclude, sorted(loadimages(folderpath))), desc="scanning"
        )
    ]
    zip_contents = [
        df(
            pd.concat([row[1], pd.Series(scan_bytes(row[1]["bsheets"]))])
            for row in itm.sort_values("filename").iterrows()
        )
        for itm in tqdm(scanned_zip, desc="sniffing")
    ]
    return zip_contents


# def repair_dataset(folderpath:Union[str, os.PathLike],
#                    dst_path:Union[str, os.PathLike]=None,
#                    exclude:Union[str, list, tuple]=[])->None:
#     sctest = pd.concat([itm.drop([row[0] for row in itm.iterrows()
#                         if 'empty_datas' in row[1].values],
#                        axis=0) for itm in
#               scansniff_zip(folderpath, exclude)],
#                        ignore_index=True).sort_values('filename')

#     sctest[['newsheets', 'dst_path']] = \
#         [(mkfrombytes(row[1].bsheets, row[1].encoding,
#                       row[1].delimiter, row[1].dup_index)
#                       if not row[1].dup_index else
#                       fix_dupindex(mkfrombytes(row[1].bsheets, row[1].encoding,
#                                                row[1].delimiter, row[1].dup_index),
#                                    row[1].has_header, row[1].delimiter),
#                       pjoin([dst_path if dst_path else folderpath][0],
#                             os.path.splitext(row[1].filename)[0]+'.tsv'))
#                      for row in tqdm(sctest.iterrows(), desc = 'repairing')]

#     [stream2file(row[1].newsheets, row[1].dst_path)
#      for row in tqdm(sctest.iterrows(), desc = 'saving')]


def repair_dataset(
    folderpath: Union[str, os.PathLike],
    dst_path: Union[str, os.PathLike] = None,
    exclude: Union[str, list, tuple] = [],
) -> None:
    sctest = pd.concat(
        [
            itm.drop(
                [row[0] for row in itm.iterrows() if "empty_datas" in row[1].values],
                axis=0,
            )
            for itm in scansniff_zip(folderpath, exclude)
        ],
        ignore_index=True,
    ).sort_values("filename")

    sctest[["newsheets", "dst_path"]] = [
        itm[1]
        for itm in sorted(
            [
                (
                    row[1].filename,
                    (
                        mkfrombytes(
                            row[1].bsheets,
                            row[1].encoding,
                            row[1].delimiter,
                            row[1].dup_index,
                        )
                        if not row[1].dup_index
                        else fix_dupindex(
                            mkfrombytes(
                                row[1].bsheets,
                                row[1].encoding,
                                row[1].delimiter,
                                row[1].dup_index,
                            ),
                            row[1].has_header,
                            row[1].delimiter,
                        ),
                        pjoin(
                            [dst_path if dst_path else folderpath][0],
                            os.path.splitext(row[1].filename)[0] + ".tsv",
                        ),
                    ),
                )
                for row in tqdm(sctest.iterrows(), desc="repairing")
            ]
        )
    ]

    [
        stream2file(row[1].newsheets, row[1].dst_path)
        for row in tqdm(sctest.iterrows(), desc="saving")
    ]
