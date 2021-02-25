#!/usr/bin/env python3

import os
import pandas as pd
import regex as re
import shutil

from chardet import UniversalDetector as udet
from collections import Counter
from os.path import expanduser as xpu
from os.path import basename as bname
from os.path import dirname as dname

from os.path import join as pjoin
from pandas import DataFrame as df
from tqdm import tqdm
from typing import Union
from zipfile import ZipFile

from removeEmptyFolders import removeEmptyFolders

from inspect_misc_text import evenodd
from inspect_misc_text import filter_lst_exc
from inspect_misc_text import filter_lst_inc
from inspect_misc_text import filter_lst_inc
from inspect_misc_text import no_ascii

def getnametuple(myzip): 
    '''
    Adjustment to ZipFile.namelist() function to prevent MAC-exclusive
    '__MACOSX' and '.DS_Store' files from interfering.
    Only necessary for files compressed with OS 10.3 or earlier.
    Source: https://superuser.com/questions/104500/what-is-macosx-folder
    Command line solution:
        ``` zip -r dir.zip . -x ".*" -x "__MACOSX"
    Source: https://apple.stackexchange.com/questions/239578/compress-without-ds-store-and-macosx
    '''
    return tuple(sorted(list(itm for itm in
                             myzip.namelist()
                             if  bname(itm).startswith('.') == False \
                             and '__MACOSX' not in itm \
                             and 'textClipping' not in itm
                             and itm != os.path.splitext(bname(dname(itm)))[0]+'/')))

def get_all_bitems(inpt:bytes, encoding:str=None):
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]  
    return [line.replace(bytes('\x00', encoding),
                         bytes('n\a', encoding)).split()
            for line in bytes('\n', encoding).join(
                inpt.splitlines()).split( bytes('\n', encoding))]

def get_delimiter(inpt:bytes, encoding:str=None):
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    seps = Counter(pd.Series(pd.Series(pd.Series(next((
               re.sub(bytes('|', encoding).join(map(re.escape, itm[1])),
               bytes('|', encoding), itm[0])
               for itm in tuple(zip(inpt.splitlines(),
               [line.replace(bytes('\x00', encoding),
                         bytes('', encoding)).split()
                for line in bytes('\n', encoding).join(
                inpt.splitlines()).split( bytes('\n', encoding))]))))).unique().max().split(
                   bytes('\\', encoding))).unique()[0].split(
                       bytes('|', encoding))[1:], dtype='object').unique()).most_common(1)
    if seps:
        return [seps[0][0] if seps[0][0] else bytes('\s', encoding)][0]
    else:
        return bytes('\s', encoding)

def get_bzip_enc(inpt:bytes):
    encodings, detector = [], udet()
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
    return detector.result['encoding']

def get_lineterminator(inpt:bytes)->bytes:
    return pd.Series(next((itm[0].strip(itm[1])
                           for itm in
                           tuple(zip(inpt.splitlines(keepends=True),
                                     inpt.splitlines()))))).unique()[0]

def get_has_header(inpt:bytes, encoding=None)->bool:
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return bool(inpt[0] not in bytes('.-0123456789', encoding))

    
def get_widths(inpt:bytes, encoding=None, hdr=None):
    lines = [inpt.splitlines()[1:] if hdr else inpt.splitlines()][0]
    encoding = [encoding if encoding else get_bzip_enc(inpt)][0]
    return int(pd.Series(len(line) for line in
                          lines).fillna(1).max())
    
    

def get_zip_contents(archv_path:Union[os.PathLike, str],
                     ntpl=[], exclude=[], to_close:bool=True)->object:
    myzip = ZipFile(archv_path)
    ntpl = [ntpl if ntpl else getnametuple(myzip)][0]    
    if exclude:
        ntpl = filter_lst_exc(exclude, getnametuple(myzip))
    vals = df(tuple(dict(zip(evenodd(itm)[0], evenodd(itm)[1])) for itm
                    in tuple(tuple(no_ascii(repr(itm.lower())).strip().replace(
               "'", "").replace("'",'').replace(
                   '=',' ')[:-2].split())[1:]
               for itm in set(repr(myzip.getinfo(itm)).strip(
                   ' ').replace(itm, itm.replace(' ', '_')) if ' ' in
                       itm else repr(myzip.getinfo(itm)).strip(
                           ' ') for itm in ntpl))), dtype='object').sort_values(
                               'filename').reset_index(drop=True)
    vals[['src_name', 'ext']] = [(nm, os.path.splitext(nm)[1])
                                    for nm in ntpl]
    vals['filename'] = [row[1].filename.replace('/', '_')
                        for row in vals.iterrows()]
    if to_close:
        myzip.close()
        return vals
    else:
        return (myzip, vals)

def scan_zip_contents(archv_path:Union[os.PathLike, str],
                      ntpl=[], to_xtrct=[], exclude=[],
                      to_close:bool=True, withbytes:bool=False,
                      dst_path: Union[os.PathLike, str]=None)->object:
    myzip, vals = get_zip_contents(archv_path, ntpl,
                                   exclude, to_close=False)
    if exclude:
        vals = vals.drop([row[0] for row in vals.iterrows()
                          if row[1].filename not in filter_lst_exc(
                              exclude, vals.filename)], axis=0)
    if to_xtrct:
        dst_path = [dst_path if dst_path
                    else pjoin(dname(archv_path),
                               os.path.splitext(bname(archv_path))[0])][0]
        os.makedirs(dst_path, exist_ok = True)
        xtrct_lst = vals.loc[[row[0] for row in vals.iterrows()
                              if row[1].filename in
                              filter_lst_inc(to_xtrct,
                                             list(vals.filename),
                                            sort=True)]]
        [shutil.move(myzip.extract(member=row[1].src_name,
                       path=dst_path), pjoin(dst_path, row[1].filename))
         for row in tqdm(xtrct_lst.iterrows(), desc = 'extraction')]
        vals = vals.loc[[row[0] for row in vals.iterrows()
                         if row[1].filename not in xtrct_lst.values]]
        removeEmptyFolders(dst_path, False)
    if withbytes:
        vals['bsheets'] = [myzip.open(row[1].src_name).read().lower()
                           for row in vals.iterrows()]
    if to_close:
        myzip.close()
    return vals.reset_index(drop = True)

def scan_archv(inpt:bytes)->dict:
    encod = get_bzip_enc(inpt)
    hdr = get_has_header(inpt, encod)
    return  dict(zip(('encoding', 'delimiter', 'has_header',
                      'width', 'nrows'),
                     (encod, get_delimiter(inpt, encod),
                      hdr, get_widths(inpt, encod, hdr),
                      len(inpt.splitlines()))))

def force_utf8(inpt: bytes, encoding:str)->bytes:
    return inpt.replace('0xff'.encode(encoding), ''.encode(encoding)).replace(
               '\x00'.encode(encoding), ''.encode(encoding)).decode(
                   'ascii', 'replace').replace('�', '').strip().encode('utf8')

def mkfrombytes(inpt:bytes, encoding:str, delimiter:bytes, hdr:bool)->object:
    return [re.sub(b'\s{2,}', b'\t',
                   re.sub(delimiter, b'\t',
                          re.sub(delimiter + b'{2,}',
                                 delimiter + b'n\a' + delimiter,
                                 line))).strip().replace(b' ', b'_').split(b'\t')
            for line in force_utf8(inpt, encoding).splitlines()]

