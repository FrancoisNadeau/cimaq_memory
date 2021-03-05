# #!/usr/bin/env python3
#
# import collections
# import csv
# import glob
# import gzip
# import io
# import itertools
# import json
# import lzma
# import nibabel as nib
# import nilearn
# import numpy as np
# import os
# import pandas as pd
# import pprint
# import random
# import re
# import reprlib
# import scipy
# import shutil
# import string
# import sys
# import tarfile
# import zipfile
#
# from collections import Counter
# from collections import OrderedDict
# from functools import reduce
# from io import StringIO
# from numpy import nan as NaN
# from operator import itemgetter
# from os import getcwd as cwd
# from os import listdir as ls
# from os.path import basename as bname
# from os.path import dirname as dname
# from os.path import expanduser as xpu
# from os.path import join
# from os.path import splitext
# from pandas import DataFrame as df
# from tabulate import tabulate
# from tqdm import tqdm
# from typing import Sequence
# from typing import Union
# from removeEmptyFolders import removeEmptyFolders

########### Miscellaneous '.txt' Files Parser #################################


# def get_dialect(filename, encoding: str = None) -> object:
#     """Source: https://wellsr.com/python/introduction-to-csv-dialects-with-the-python-csv-module/#DialectDetection
#     Description: Prints out all relevant formatting parameters of a dialect"""
#     encoding = [encoding if encoding else get_bzip_enc(filename)][0]
#     with open(filename, encoding=encoding) as src:
#         dialect = csv.Sniffer().sniff(src.readline())
#         src.seek(0)
#         #         lines4test = list(src.readlines())
#         src.seek(0)
#         valuez = [
#             bname(filename),
#             dialect.delimiter,
#             dialect.doublequote,
#             dialect.escapechar,
#             dialect.lineterminator,
#             dialect.quotechar,
#             dialect.quoting,
#             dialect.skipinitialspace,
#         ]
#         cnames = [
#             "fname",
#             "delimiter",
#             "doublequote",
#             "escapechar",
#             "lineterminator",
#             "quotechar",
#             "quoting",
#             "skipinitialspace",
#         ]
#         dialect_df = pd.Series(valuez, index=cnames)
#         src.close()
#         return dialect_df


# def splitrows(inpt):
#     evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
#     evvals, odvals = itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)
#     return evvals == odvals


# def evenodd_col2(inpt):
#     evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
#     evvals, odvals = listat(evlst, inpt), listat(odlst, inpt)
#     return df(evvals), df(odvals)
#
#
# def dupvalues(inpt):  # Works well
#     """
#     Adapted from
#     Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
#     """
#     evlst, odlst = evenodd_col2([itm[0] for itm in enumerate(inpt)])
#     evvals = itemgetter(*[itm[1] for itm in enumerate(evlst)])(inpt)
#     odvals = itemgetter(*[itm[1] for itm in enumerate(odlst)])(inpt)
#     return df(evvals, dtype="object").values == \
#         df(odvals, dtype="object").values


###############################################################################

#
# def get_doublerows(inpt: object) -> list:  # Works well
#     return [itm[0] for itm in enumerate(df(inpt).iteritems()) if splitrows(itm[1][1])]
#
#
# def dupcols(inpt: object) -> object:
#     """
#     Adapted from
#     Source: https://stackoverflow.com/questions/18272160/access-multiple-elements-of-list-knowing-their-index
#     """
#     msk = df(dupvalues(inpt), dtype="object")
#     boolcols = [all(itm[1]) for itm in msk.iteritems()]
#     return msk.loc[:, boolcols]
#
#
# def get_singlerows(inpt: object):
#     rowbreaks = [
#         item[0] for item in enumerate(inpt.iteritems()) if not splitrows(item[1][1])
#     ]
#     return inpt[tuple(itemgetter(*rowbreaks)(tuple(inpt.columns)))]
#
#
# def splitrows2vals(inpt):
#     #     inpt = [line[0] for line in inpt]
#     evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
#     evvals, odvals = itemgetter(*evlst)(inpt), itemgetter(*odlst)(inpt)
#     return evvals == odvals
