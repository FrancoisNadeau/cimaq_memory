#!/usr/bin/env python

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
    for fpath in filelist:
        detector = udet()
        detector.reset()
        with (open(fpath), 'r') as opf:
            detector.feed(opf)
            detector.close()
            results.append((bname(fpath), detector.result['encoding']))
    return results

def main():
    NEW_sniffer2()

if __name__ == '__main__':
    main()
