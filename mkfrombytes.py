#!/usr/bin/env python3

import chardet
import itertools
import gzip
import io
import itertools
import json
import lzma
import numpy as np
import os
import pandas as pd
import regex as re
import reprlib
import string
import struct
import shutil
import sys
import tarfile
import zipfile

from chardet import UniversalDetector as udet
from collections import Counter
from functools import reduce
# from io import BytesIO
# from io import StringIO
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

import sniffbytes as snif
from sniffbytes import get_bytes
from sniffbytes import get_bencod
from sniffbytes import get_delimiter
from sniffbytes import get_bytes
from sniffbytes import get_dup_index
from sniffbytes import get_lineterminator
from sniffbytes import fix_na_reps
from sniffbytes import fix_dup_index

def mkfrombytes(inpt: Union[bytes, str, os.PathLike],
                encoding: str = None,
                delimiter: bytes = None,
                hdr: bool = False,
                dup_index: bool = None,
                new_sep: bytes = b"\t") -> bytes:
    inpt = get_bytes(inpt)
    encoding = [encoding if encoding
                else get_bencod(inpt)][0]
    delimiter = [delimiter if delimiter
                 else get_delimiter(inpt)][0]
    hdr = [hdr if hdr else get_has_header(inpt)][0]
    lterm = [lterm if lterm else get_lineterminator(inpt)][0]
    dup_index = [dup_index if dup_index
                 else get_dup_index(inpt)][0]
    if not dup_index:
        fix_na_reps(inpt, encoding, delimiter, lterm)
#         try:
#             return (
#                 b"\n".join(
#                     [
#                         re.sub(
#                             b"\s{2,}",
#                             new_sep,
#                             re.sub(
#                                 delimiter,
#                                 new_sep,
#                                 re.sub(
#                                     delimiter + b"{2,}",
#                                     delimiter + b"NaN" + delimiter, line
#                                 ),
#                             ),
#                         )
#                         .strip()
#                         .replace(b" ", b"_")
#                         .replace(b"\x00", b"NaN")
#                         for line in force_utf8(strip_null(inpt, encoding), encoding).splitlines()
#                     ]
#                 )
#                 .replace(delimiter, new_sep)
#                 .decode()
#                 .encode()
#             )
#         except:
#             return strip_null(inpt, encoding)
#     else:
#         return force_utf8(strip_null(fix_dup_index(inpt,
#                                                    encoding, hdr, delimiter),
#                                      encoding), encoding)

def main():    
    if __name__ == "__main__":
        mkfrombytes(inpt, encoding,
                 delimiter, hdr, dup_index)
