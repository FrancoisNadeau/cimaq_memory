#!/usr/bin/env python3

import os
import pandas
from zipfile import ZipFile
from pandas import DataFrame as df
from inspect_misc_text import evenodd
from inspect_misc_text import no_ascii
###############################################################################

def get_zipinfos(fpath):
    with ZipFile(fpath, 'r') as myzip:
        encodings, bsheets, lterms = [], [], []
        namelist = getnamelist(fpath)
        contents = df(tuple(dict(zip(evenodd(itm)[0], evenodd(itm)[1])) for itm
                            in tuple(tuple(no_ascii(repr(itm)).strip().replace(
                       "'", "").replace("'",'').replace(
                           '=',' ')[:-2].split())[1:]
                       for itm in set(repr(myzip.getinfo(itm)).strip(' ').replace(
                                      itm, itm.replace(' ', '_')) 
                                      if ' ' in itm else repr(myzip.getinfo(itm)).strip(' ')
                                      for itm in namelist))))
        contents['fpaths'] = [join(os.path.splitext(fpath)[0], fname)
                              for fname in contents.filename]
        contents = contents.sort_values('filename')
        contents['src_names'] = namelist
        contents['exts'] = [os.path.splitext(filename)[1]
                            for filename in contents.filename]
        for row in contents.iterrows():
            '''https://www.prepressure.com/pdf/basics/fileformat#:~:text=PDF%20files%20are%20either%208,to%20create%20the%20PDF%20file).'''
            with myzip.open(row[1]['src_names']) as myfile:
                bsheets.append((row[1]['filename'], myfile.read()))
                myfile.seek(0)                   
                encod = chardet.detect((myfile.read()))['encoding']
                if encod == None:
                    encod = 'ascii'
                myfile.seek(0)                
                encodings.append((row[1]['filename'], encod))
                myfile.close()
        contents['encoding'] = [itm[1] for itm in sorted(encodings)]
        contents['bytes_sheets'] = [itm[1] for itm in sorted(bsheets)]
        contents['lineterminator'] = [[line for line in
                                       row[1]['bytes_sheets'].splitlines(
                                           keepends=True)][0].strip([line for line in
                                             row[1]['bytes_sheets'].splitlines()][0])
                                      for row in contents.iterrows()]
        contents['delimiter'] = [[csv.Sniffer().sniff(row[1]['bytes_sheets'].splitlines(
                                    )[0].decode(row[1]['encoding'])).delimiter]
                                 for row in contents.iterrows()]
        contents['n_lines'] = [len(row[1]['bytes_sheets'].splitlines())
                               for row in contents.iterrows()]
        myzip.close()
    return contents.reset_index(drop=True)
