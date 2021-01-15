#!/usr/bin/env python
# encoding: utf-8

import zipfile
from chardet import UniversalDetector as udet
from os import listdir as ls
from os.path import expanduser as xpu
from os.path import join
from pandas import DataFrame as df


def sniffzipped(zipindir="~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/zipped_eprime"):
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
    zipindir = xpu(zipindir)
    results = []
    infos = []
    zfpaths = [join(zipindir, zfname) for zfname in ls(zipindir)]
    for zfpath in zfpaths:
        with open(zipfile.ZipFile(zfpath), 'r') as archv:
            info = [dict(archv.getinfo(join(zfpath, archv, name)))
                    for name in archv.namelist()]
            infos.append(info)
            detector.reset
            rezz = []
            for line in archv.readlines():
                detector.feed(line)
                if detector.done:
                    rezz.append(detector.result)
                    detector.close()
                    break

            results.append(rezz)
            archv.close()
    analysis = tuple(zip(sorted(results), sorted(infos)))
    print(analysis)
    return analysis

def main():
    sniffzipped()

if __name__ == '__main__':
    main()
