#!/usr/bin/env python

import chardet
import os
from chardet import detect
from os.path import basename as bname

def get_encoding(sheetlist):
    ''' Detect character encoding for files not encoded
        with current encoding type ('UTF-8').

        Parameters
        ----------
        sheetlist: list of paths or os.path-like objects pointing
                    to a document file (various extensions supported,
                    see online documentation at
                    https://chardet.readthedocs.io/en/latest/

        Returns
        -------
        encodings: list of (sheet basename, encoding dict) tuples
                    for each sheet in 'sheetlist'
    '''

    sheetlist = sorted(sheetlist)
    results = []
    for sheetpath in sheetlist:
        bsheet = open(sheetpath, "rb").read()
        rezz = chardet.detect(bsheet)
        results.append((rezz))
    encodings = dict(zip(sheetlist, results))
    
    return encodings
    
def main():
    get_encoding()
if __name__ == '__main__':
    main()
