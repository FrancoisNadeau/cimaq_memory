#!/usr/bin/env python3
""" Sniffbytes """

import os
import string
import sys
from collections import Counter
from functools import reduce
from os.path import basename as bname
from os.path import dirname as dname
from os.path import join as pjoin
from typing import Sequence
from typing import Union
from unidecode import unidecode
import numpy as np
import pandas as pd
import regex as re
from chardet import UniversalDetector as udet
from pandas import DataFrame as df

def loadimages(indir: Union[os.PathLike, str]) -> list:
    """ Lists the full relative path of all '.jpeg' files in a directory.
        Only lists files, not directories.
        ----------------------------------
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
    """ Returns unidimensional list from nested list using list comprehension.
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
        flatlst: unidimensional list """
    return [bottomElem for sublist in nested_seq
            for bottomElem in (flatten(sublist) if
                               (isinstance(sublist, Sequence) \
                                and not isinstance(sublist, str))
                               else [sublist])]

def loadfiles(pathlist: Union[list, tuple]) -> object:
    """ Returns a pd.DataFrame with columns
        -----------------------------------
        'filename': name of file without extension,
        'ext': file extension,
        'parent': parent directory name,
        'fpaths': path to file """
    return (df(((bname(sheet).split(".", 1)[0],
                 os.path.splitext(sheet)[1],
                 bname(dname(sheet)), sheet,)
                for sheet in pathlist),
                dtype = object,
                columns=["filename", "ext", "parent", "fpaths"],
        ).sort_values("filename").reset_index(drop=True))

def evenodd(inpt) -> tuple:
    """ Returns a tuple containg all (even items, odd items) from 'inpt' """
    eveseq = tuple(ele[1] for ele in enumerate(inpt) if ele[0] % 2 == 0)
    oddseq = tuple(ele[1] for ele in enumerate(inpt) if ele[0] % 2 != 0)
    return (eveseq, oddseq)

def filter_lst_exc(
    exclude: Union[list, tuple],
    str_lst: Union[list, tuple],
    sort: bool = False
) -> list:
    """
    Returns a tuple of elements excluding all items
    matching patterns in 'exclude'
    ------------------------------
    Parameters
    ----------
    exclude: patterns susceptible to return a match among items in 'str_lst'
    str_lst: list of items to be filtered
    """
    outlst = [itm for itm in str_lst if
              all(sub not in itm for sub in exclude)]
    return [sorted(outlst) if sort else outlst][0]


def filter_lst_inc(
    include: Union[list, tuple],
    str_lst: Union[list, tuple],
    sort: bool = False
) -> list:
    """
    Returns a tuple of elements including only
    items matching patterns in 'include'
    Parameters
    ----------
    include: patterns susceptible to return a match among items in 'str_lst'
    str_lst: list of items to be filtered
    """
    outlst = [itm for itm in str_lst if
              any(sub in itm for sub in include)]
    return [sorted(outlst) if sort else outlst][0]

def find_key(input_dict: dict, value):
    """ Shortcut to find a value's correspond ing key in a dict """
    return next((k for k, v in input_dict.items() if v == value), None)

def megamerge(dflist: list, howto: str, onto: str = None) -> object:
    """ Returns a pd.DataFrame made from merging the frames in 'dflist' """
    return reduce(lambda x, y: pd.merge(x, y, on=onto,
                                        how=howto).astype("object"), dflist)

def get_bytes(inpt: Union[bytes, bytearray, str, os.PathLike, object]):
    """ Returns a bytes object from 'inpt', no matter what 'inpt' is.
        Description
        -----------
        If inpt is a bytes (any kind) object:
            Returns inpt as is;
        If inpt is a string (which is not a file or directory path)
            Returns a bytes (UTF-8) version of inpt;
        If inpt is a path pointing to a file:
            Returns the bytes contained in that file
        *If the return value is a single or empty-byte object,
         returns b"1" (utf8 bytes representation of the number one) """
    if isinstance(inpt, (bytes, bytearray)):
        outpt = [inpt.lower() if bool(len(inpt.splitlines()) > \
                  0 and inpt is not None) else b"1"][0]
    if isinstance(inpt, str) and os.path.isfile(inpt):
        with open(inpt, "rb", buffering = 0) as myfile:
            outpt = myfile.read().lower()
            outpt = [outpt if bool(len(outpt.splitlines()) > 1)
                     else b"1"][0]
            myfile.close()
    if isinstance(inpt, str) and not os.path.isfile(inpt):
        outpt = inpt.encode()
    return outpt


def get_bencod(
    inpt: Union[bytes, bytearray, str, os.PathLike, object]
) -> str:
    ''' Returns the character encoding of 'inpt' as a string
        ----------------------------------------------------
        Parameters
        ----------
        inpt: Bytes from memory or file path pointing to a file
              file object ot be read as raw stream of bytes
              in native file character encoding '''
    inpt = get_bytes(inpt)
    detector = udet()
    detector.reset()
    while True:
        next((detector.feed(line) for line in inpt.splitlines()))
        if (
            not detector.done \
            and not detector.result \
            and detector.result["confidence"] > 0.75
            and detector.result["encoding"] is not None
        ):
            continue
        else:
            break
        break
    detector.close()
    return detector.result["encoding"]

def get_has_header(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None
) -> bool:
    """ Returns True if 1st line of inpt is a header line
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes)
        - Optional
        ----------
        encoding: Character encoding of the bytes in buffer """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    return [
        bool(inpt[0] not in
             bytes(".-0123456789", encoding))
        if len(inpt) > 1 else False
    ][0]

def get_widths(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None, has_header: bool = None
) -> Union[str, int]:
    """ Returns an integer corresponding to the longest line in
        bytes buffer that is not a header, which could include
        extra bytes such as commments
        -----------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes)
        ----------------------------------
        - Optional
        ----------
        encoding: Character encoding of the bytes in buffer """
    inpt = get_bytes(inpt).replace(
               "\x00".encode(encoding), "".encode(encoding))
    lines = [inpt.splitlines()[1:] if has_header else inpt.splitlines()][0]
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    return pd.Series(len(line) for line in lines).fillna(1).max()

def get_lineterminator(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None
) -> bytes:
    """ Returns the character used as line terminator within
        the bytes stream buffer in native character encoding

        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes) """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    linterminator = pd.Series(
        next(
            (
                itm[0].strip(itm[1])
                for itm in tuple(zip(inpt.splitlines(keepends=True),
                                     inpt.splitlines()))
            )
        )
    ).unique()[0]
    return [linterminator if linterminator != "".encode(encoding)
            else '\n'.encode(encoding)][0]

def get_delimiter(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None,
    lineterminator: bytes = None
) -> bytes:
    """ Returns the character used as delimiter within
        the bytes stream buffer in native character encoding
            - Replaces csv.Sniffer,
              which raises an error upon failure
                  - Failure happens frequently for files
                    containing any writing or formatting mistake
        --------------------------------------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes)
        ----------------------------------
        - Optional
        ----------
        encoding: Character encoding of the bytes in buffer """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    delimiters = Counter(
        pd.Series(
            pd.Series(
                pd.Series(
                    next(
                        (
                            re.sub(
                                bytes("|", encoding).join(
                                    map(re.escape, itm[1])),
                                bytes("|", encoding),
                                itm[0],
                            )
                            for itm in tuple(
                                zip(
                                    inpt.splitlines(),
                                    [
                                        line.replace(
                                            bytes("\x00", encoding),
                                            bytes("", encoding)
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
    ).most_common(1).__iter__()
    try:
        delimiter = list(delimiters)[0][0]
    except IndexError:
        delimiter = [lineterminator if lineterminator is not None
                     else get_lineterminator(inpt, encoding)][0]
    return [delimiter if delimiter != b"" else " ".encode(encoding)][0]


def get_dup_index(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None,
    has_header: bool = None,
) -> bool:
    """ Returns True if the first item of each even and each
        odd line is repeated. Returns False otherwise or upon IndexError.
        As IndexError is raised when trying to access values by an index out
        of a sequence boundairies, IndexError indicates single-byte files.
        Being a single byte, it can't be a duplicate index.
        ---------------------------------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes).
        -----------------------------------
        - Optional
          --------
        has_header: True if first line is a header, else False
        delimiter: Bytes (in native file encoding) representation
                   of the value used as delimiter. """
    inpt = get_bytes(inpt)
    bytelines = [inpt.splitlines() if not
                 [has_header if has_header is not None else
                  get_has_header(inpt, encoding)][0]
                  else inpt.splitlines()[1:]][0]
    ev_itms, od_itms = evenodd([line.split() for line in bytelines])
    try:
        return bool([line[0] for line in ev_itms] == \
                    [line[0] for line in od_itms])
    except IndexError:
        return False

def get_nfields(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None,
    has_header: bool = None
) -> bytes:
    """ Returns a bytes representation of an integer corresponding
        to the maximal number of fields in the bytes stream lines
        for lines that are not a header.
        --------------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes).
        -----------------------------------
        - Optional
          --------
        has_header: True if first line is a header, else False. """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    has_header = [has_header if has_header is not None else
                  get_has_header(inpt, encoding)][0]
    inpt = [inpt.splitlines()[1:] if has_header else
            inpt.splitlines()][0]
    return pd.Series(len(line.split())
                      for line in inpt).max()

def sniff_bytes(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None,
    has_header: bool = None,
) -> dict:
    """ Returns a dictionary containing informations about datas from
        a readable file or buffer of raw bytes.
        ---------------------------------------
        Order is as folllows:
            ("encoding", "delimiter", "has_header", "dup_index",
             "lineterminator", "nfields", "width", "nrows").
        ----------------------------------------------------
        Information is similar to csv.dialect objects.
        The outout is designed to work well with common data structures,
        including, bu not restricted to:
            - CSV, Pandas, _io buffers, arrays etc.
        -------------------------------------------
        See each function's help details individually:
            inpt = help(sniffer.get_bytes)
            encoding = help(sniffer.get_bencod)
            has_header = help(sniffer.get_has_header)
            delimiter = help(sniffer.get_delimiter)
            lineterminator = help(sniffer.get_lineterminator)
            dup_index = help(snif.dup_index) """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    has_header = [has_header if has_header is not None
                  else get_has_header(inpt, encoding)][0]
    return dict(zip(
                ("encoding", "delimiter", "has_header", "dup_index",
                  "lineterminator", "width", "nrows"),
                (encoding, get_delimiter(inpt, encoding),
                 has_header, get_dup_index(inpt, encoding, has_header),
                 get_lineterminator(inpt, encoding),
                 get_widths(inpt, encoding, has_header),
                 len(inpt.splitlines()),
                ),
            )
        )

def fix_na_reps(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None,
    delimiter: bytes = None,
    lineterminator: bytes = None
) -> bytes:
    """ Returns a version of the bytes buffer replacing any missing 'missing'
        values by automatically.
        To do so, the np.nan value, padded between whitespaces - all
        converted into native file encoding, are inserted where two or
        more consecutive delimiters are found.
        --------------------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes).
        -----------------------------------
        - Optional
          --------
        encoding: Character encoding of the bytes in buffer.
        delimiter: Bytes (in native file encoding) representation
                   of the value used as delimiter.
        lineterminator: Bytes (in native file encoding) representation
                        of the value used as line terminator. """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    delimiter = [delimiter if delimiter else get_delimiter(inpt, encoding)][0]
    return [lineterminator if lineterminator else
            get_lineterminator(inpt, encoding)][0].join(
                re.sub(delimiter+'{2,}'.encode(encoding),
                       delimiter+str(np.nan).encode(encoding)+delimiter,
                       line) for line in inpt.splitlines())

def fix_dup_index(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None
) -> bytes:
    """ Fixes files where indexes are duplicated.
        -----------------------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes).
        -----------------------------------
        - Optional
        ----------
        encoding: Character encoding of the bytes in buffer.
        delimiter: Bytes (in native file encoding) representation
                    of the value used as delimiter. """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    evdf, oddf = (df((line.split() for line in lines),
                     dtype = object) for lines
                  in evenodd(inpt.splitlines()))
    booltest = [itm[0] for itm in enumerate(
                   tuple(zip([itm[1] for itm in
                              evdf.iteritems()],
                              [itm[1] for itm in
                               oddf.iteritems()])))
                if all(itm[1][0].values == itm[1][1].values)]
    datas = pd.concat((evdf[booltest],
                       pd.concat(list(itm[1] for itm in
                                      evdf.iteritems())[booltest[-1]+1:-1],
                                 axis = 1),
                       pd.concat(list(itm[1] for itm in
                                      oddf.iteritems())[booltest[-1]+1:],
                                 axis = 1)),
                      axis = 1)
    try:
        return '\n'.encode(encoding).join('\t'.encode(encoding).join(
            itm if isinstance(itm, bytes) else str(np.nan).encode()
            for itm in row[1].values.tolist()) for row in datas.iterrows())
    except IndexError:
        return inpt

def clean_bytes(
    inpt: Union[bytes, bytearray, str, os.PathLike, object],
    encoding: str = None,
    has_header: bool = None,
    delimiter: bytes = None,
    lineterminator: bytes = None,
    dup_index: bool = None,
    **kwargs: Union[bytes, bytearray, str, dict, object, map,
                    tuple, os.PathLike, pd.DataFrame]
) -> bytes:
    """ Returns a clean (suitable for StringIO and Pandas modules)
        bytes stream buffer with fixed 'missing' missing values.
        --------------------------------------------------------
        Takes into account:
            - Incorrect missing values representation
            - Duplicated indexes
            - Inconsistent delimiters
            - Within-values inconsistencies
                  - (e.g. using a variable amount of whitespaces
                     to delimiterarate values within a same file or stream.
            - If file has a header row with labels or not
            - Variable source or native character encodings
        Bonus: Files can be read from ZipFile archives
            - See 'scanzip.py'
        ----------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes).
        -----------------------------------
        - Optional
        ----------
        encoding: Character encoding of the bytes in buffer.
        has_header: True if first line is a header, else False.
        delimiter: Bytes (in native file encoding) representation
                   of the value used as delimiter.
        lineterminator: Bytes representation in native file encoding
                        of the line termination character.
        dup_index: True if 'inpt' has duplicated index values, else False. """
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    has_header = [has_header if has_header is not None else
                                get_has_header(inpt, encoding)][0]
    delimiter = [delimiter if delimiter is not None else
                 get_delimiter(inpt, encoding)][0]
    lineterminator = [lineterminator if lineterminator else
                      get_lineterminator(inpt, encoding)][0]
    dup_index = [dup_index if dup_index is not None else
                 get_dup_index(inpt, encoding, has_header)][0]
    newsheet = b'\n'.join([b'\t'.join(itm.strip(b" ") for itm in
                                      re.sub(b" " + b"{2,}",
                                             b" "+delimiter + b" ",
                                             line).split(delimiter))
                           for line in
                           fix_na_reps(get_bytes(inpt).lower(),
                                       encoding, delimiter,
                                       lineterminator).decode(
                                           "utf8", "replace").replace(
                                               "�", "").strip().encode(
                                                   "utf8").splitlines()])
    return [fix_dup_index(newsheet, encoding)
            if dup_index else newsheet][0]

def bytes2df(inpt: Union[bytes, bytearray, str, os.PathLike, object],
             encoding: str = None,
             delimiter: bytes = None,
             has_header: bool = None,
             **kwargs: Union[bytes, bytearray, str, dict, object, map,
                             list, tuple, os.PathLike, pd.DataFrame]
             ) -> pd.DataFrame:
    """ Converts a bytes object to a pd.DataFrame object
        ------------------------------------------------
        Parameters
        ----------
        inpt: Bytes stream from buffer or file
                - See help(snif.get_bytes).
        -----------------------------------
        - Optional
        ----------
        encoding: Character encoding of the bytes in buffer.
        has_header: True if first line is a header, else False.
        delimiter: Bytes (in native file encoding) representation
                    of the value used as delimiter.
        dup_index: True if 'inpt' has duplicated index values, else False.
        lineterminator: Bytes representation in native file encoding
                        of the line termination character. """
    return [df((line.split('\t') for line in unidecode(
                  clean_bytes(inpt, **kwargs).decode()).split('\n')),
                 dtype = object).T.set_index(0, drop = True).T
             if [has_header if has_header is not None
                 else get_has_header(inpt)][0] else
        df((line.split('\t') for line in unidecode(
                 clean_bytes(inpt, **kwargs).decode()).split('\n')),
                                   dtype = object)][0]

def stream2file(inpt: Union[bytes, bytearray, str, os.PathLike, object],
                dst_path: Union[str, os.PathLike]) -> None:
    """ Save bytes stream buffer to file.
        ---------------------------------
        Parameters
        ----------
        inpt: Bytes stream buffer or file path to read bytes from.
        dst_path: Path pointing to desired save location """
    with open(dst_path, "wb") as binary_file:
        binary_file.write(inpt)
        binary_file.close()

########################## Unused Yet #########################################
def bytes_printable(
    inpt: bytes,
    encoding: str = None
) -> bytes:
    """ Same as is_printable, but for bytes in native file encoding
        -----------------------------------------------------------
        Parameters
        ----------
        inpt: Bytes stream buffer or file path to read bytes from.
        encoding: Character encoding of the bytes in buffer. """
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    b_printable = ''.encode(encoding).join([ch.encode(encoding)
                              for ch in list(string.printable)])
    return ''.encode(encoding).join([chr(val).encode(encoding) for val in
                                     list(inpt) if chr(val).encode(encoding)
                                     in b_printable])

def force_ascii(inpt: Union[str, bytes],
                encoding: str = None) -> Union[str, bytes]:
    """ Returns a version of 'inpt' converted to ASCII encoding type
        ------------------------------------------------------------
        Parameters
        ----------
        inpt: Bytes stream buffer or file path to read bytes from.
        encoding: Character encoding of the bytes in buffer. """
    encoding = [encoding if encoding else get_bencod(inpt)][0]
    return "".encode(encoding).join(filter(lambda x: x in \
        set([chr(int.from_bytes(itm, sys.byteorder)).encode(encoding)
             for itm in [itm.encode(encoding) for itm in
                         list(string.printable)]]), inpt))

################## String Manipulation ########################################

def is_printable(astring):
    """ Removes non-ASCII characters while leaving periods and spaces """
    return ''.join(ch for ch in list(astring)
                    if ch in list(string.printable))

def make_labels(datas: Union[dict, object], var_name: Union[int, str]) -> dict:
    """ Returns dict of (key, val) pairs using 'enumerate' on possible values
        filtered by 'Counter' - can be used to map DataFrame objects -"""
    return dict(enumerate(Counter(datas[var_name]).keys(), start=1))

def letters(astring: str) -> str:
    """ Returns a new string with only alphabetical
        characters from the original string """
    return "".join([ch for ch in astring if ch.isalpha()])

def num_only(astring: str) -> str:
    """ Returns a new string with only numerical
        characters from the original string """
    return "".join(ch for ch in astring if ch.isdigit())
