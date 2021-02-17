#!/usr/bin/env python3

import os
from zipfile import ZipFile
from pandas import DataFrame as df
from inspect_misc_text import evenodd
from inspect_misc_text import no_ascii

def get_zipinfos(fpath):
    with ZipFile(fpath, 'r') as myzip:
        contents = df(tuple(dict(zip(evenodd(itm)[0], evenodd(itm)[1])) for itm
                            in tuple(tuple(no_ascii(str(itm).strip()).replace(
                       "'", "").replace("'",'').replace(
                           '=',' ')[:-1].split())[1:]
                       for itm in set(myzip.getinfo(itm)
                                      for itm in myzip.namelist() if 'MACOSX'
                                      not in itm and not itm.endswith('/')))))
        contents['exts'] = [os.path.splitext(filename)[1]
                            for filename in contents.filename]
        contents[['archv_name', 'short_names', 'fpaths']] = \
                [(os.path.dirname(fname),
                  os.path.splitext(os.path.basename(fname))[0], fpath)
                 for fname in contents.filename]
        contents = contents.sort_values('filename')
        return contents

def main():
    get_zipinfos(fpath)

if __name__ == "__main__":
    main()
