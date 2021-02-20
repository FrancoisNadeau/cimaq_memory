#!/usr/bin/env python3

from cimaq_utils import *
from cimaq_utils import loadimages
from blind_rename import *
from inspect_misc_text import *
from inspect_misc_text import no_ascii
from zipctl import uzipfiles
from get_infos import get_infos
from fix_cimaq import get_cimaq_dir_paths
# from get_zipinfos import get_zipinfos

from os.path import expanduser as xpu
from os.path import join as pjoin
from collections import OrderedDict
from zipfile import ZipFile
import clevercsv
import codecs
import googletrans

from cimaq_filter import cimaq_filter
from fix_cimaq import get_cimaq_dir_paths
from zipctl import getnamelist
from zipctl import getinfolist
from chardet import UniversalDetector as Udet
from collections import Counter

def get_all_bitems(inpt, encoding):
    return [line.replace(bytes('\x00', encoding),
                                          bytes('n\a', encoding)).split()
                             for line in bytes('\n', encoding).join(
                                 inpt.splitlines()).split(
                                     bytes('\n', encoding))]

def scan_zip(myzip, nlst):
    return df(tuple(dict(zip(evenodd(itm)[0], evenodd(itm)[1])) for itm
                    in tuple(tuple(no_ascii(repr(itm)).strip().replace(
               "'", "").replace("'",'').replace(
                   '=',' ')[:-2].split())[1:]
               for itm in set(repr(myzip.getinfo(itm)).strip(
                   ' ').replace(itm, itm.replace(' ', '_')) if ' ' in
                              itm else repr(myzip.getinfo(itm)).strip(
                                  ' ') for itm in nlst))))
###############################################################################
def scan_bzip(myzip, nlst):
    contents = scan_zip(myzip, nlst)
    contents = scan_zip(myzip, nlst)
    contents[['dst_paths', 'exts']] = \
        [(join(os.path.splitext(myzip.filename)[0], fnm),
         os.path.splitext(fnm)[1])
         for fnm in contents.filename]
    contents[['src_paths', 'src_names']] = \
        [(join(os.path.splitext(myzip.filename)[0], fnm), fnm) for fnm in nlst]
    contents = contents.sort_values('filename').reset_index(drop = True)    
    contents['bsheets'] = [myzip.open(row[1].src_names, 'r').read().lower()
                           for row in contents.iterrows()]
    return contents

def get_bzip_enc(inpt):
    encodings = []
    detector = udet()
    detector.reset()
    while True:
        next((detector.feed(line) for line in
                       inpt.splitlines()))
        if not detector.done and not detector.result:
            continue
        else:
            break
        break
    detector.close()
    return tuple(detector.result.values())[0]
   
def get_lineterminator(inpt):
    return pd.Series(next((itm[0].strip(itm[1])
                           for itm in
                           tuple(zip(inpt.splitlines(keepends=True),
                                     inpt.splitlines()))))).unique()[0]

def get_has_header(inpt, encoding=None):
    if not encoding:
        encoding = get_bzip_enc(inpt)
    else:
        encoding = encoding
    return bool(inpt[0] not in
                bytes('.-0123456789', encoding))


def get_specs(inpt):
    specnames = ['n_rows', 'row_fields', 'widths', 'item_widths']
    specs = (len(inpt.splitlines()),
             [len(line.split()) for line in inpt.splitlines()],
             [len(line) for line in inpt.splitlines()],
             [[len(itm) for itm in line.split()]
              for line in inpt.splitlines()])
    return dict(zip(specnames, specs))

def get_delimiter(inpt, encoding=None):
    if not encoding:
        encoding = get_bzip_enc(inpt)
    else:
        encoding = encoding

    seps = Counter(pd.Series(pd.Series(pd.Series(next((
               re.sub(bytes('|', encoding).join(map(re.escape, itm[1])),
               bytes('|', encoding), itm[0])
               for itm in tuple(zip(inpt.splitlines(),
               get_all_bitems(inpt, encoding)))))).unique().max().split(
                   bytes('\\', encoding))).unique()[0].split(
                       bytes('|', encoding))[1:]).unique()).most_common(1)
    if seps:
        return seps
    else:
        return [(False, False)]
    
def get_zipcontents(fpath):
    myzip = ZipFile(fpath, 'r')
    nlst = tuple(getnamelist(fpath))
    contents = scan_bzip(myzip, nlst)
    
    contents['encoding'] = [get_bzip_enc(row[1]['bsheets'])
                            for row in contents.iterrows()]

    contents['lineterminator'] = [get_lineterminator(row[1]['bsheets'])
                                  for row in contents.iterrows()]

    contents['has_header'] = [get_has_header(row[1]['bsheets'],
                                             row[1]['encoding'])
                              for row in contents.iterrows()]
    
    contents[['n_rows', 'row_fields', 'widths', 'item_widths']] = \
        [tuple(get_specs(row[1]['bsheets']).values())
         for row in contents.iterrows()]
    
    contents['delimiter'] = [get_delimiter(row[1]['bsheets'],
                                           encoding=row[1]['encoding'])[0][0]
                             for row in contents.iterrows()]

    myzip.close()
    contents = contents.drop(columns='bsheets')
    return contents
