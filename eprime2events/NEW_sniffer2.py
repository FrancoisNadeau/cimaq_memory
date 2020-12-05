#!/usr/bin/env python
# encoding: utf-8

import zipfile
from chardet import UniversalDetector as udet
from os import listdir as ls
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df


def NEW_sniffer2(filelist):
    '''
    Obtain info about files in zipped archive
     - Without requiring extraction. 
    Parameters
    ----------
        zfolder: Path or path-like object as in os.path module
        
    Returns
    -------
        infos: Dict mapped as {filenameA: infoA, 
                                  [...],
                              filenameZ: infosZ}
    Source: https://chardet.readthedocs.io/en/latest/usage.html                           
'''
    results = []
    fnames = []
    for filename in filelist:
        with zipfile.ZipFile(open(filename), 'r') as archv:
            sniffed = (chardet.detect(archv)['encoding'],
                       archv.namelist(), len(archv.namelist()))                    
            results.append(sniffed)
            detector.close()
    return results

def main():
    NEW_sniffer2()

if __name__ == '__main__':
    main()
