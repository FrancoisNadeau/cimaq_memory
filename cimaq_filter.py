#!/usr/bin/env python3

import os
from os.path import basename as bname
from os.path import dirname as dname
from os.path import expanduser as xpu
from os.path import join as pjoin
from cimaq_utils import loadimages
from fix_cimaq import get_cimaq_dir_paths

def cimaq_filter():
    ''' Removes all pratice files (and READMEs)
        since no data was recorder due
        to response keyboard problems. Both READMEs indicate
        this sole information.
        Moves unused PDF, edat2 and practice files
        to "task_files/pdf_files", "task_files/edat2_files" etc.'''
    
    indir = get_cimaq_dir_paths(cimaq_dir)[0].uzeprimes.fpaths
    indir = join(cimaq_dir, dlst['uzeprimes'])
    prfr = [file for file in loadimages(indir)
            if 'pratique' in bname(file)]
    pren = [file for file in loadimages(indir)
            if 'practice' in bname(file)]
    docxs = [file for file in loadimages(indir)
             if 'read_' in bname(file)]
    joinedlist = prfr + pren + docxs
    [os.remove(file) for file in joinedlist]
    os.makedirs(join(dname(indir), 'pdf_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'pdf_files', bname(file)))
     for file in loadimages(indir) if file.endswith('.pdf')]
    os.makedirs(join(dname(indir), 'edat2_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'edat2_files', bname(file)))
     for file in loadimages(indir) if file.endswith('.edat2')]
    os.makedirs(join(dname(indir), 'retrieval_log_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'retrieval_log_files', bname(file)))
     for file in loadimages(indir) if 'retrieval' in bname(file).split('_')[0]]
    os.makedirs(join(dname(indir), 'encoding_log_files'), exist_ok=True)
    [shutil.move(file, join(dname(indir), 'encoding_log_files', bname(file)))
     for file in loadimages(indir) if 'encoding' in bname(file).split('_')[0]]
    [os.remove(itm) for itm in loadimages(indir)
     if 'fuse_hidden0002f0fa00000022' in bname(itm)]
    [os.remove(itm) for itm in loadimages(indir)
     if bname(itm) == 'onset_event_encoding_cimaq_1234567_session1a.txt']
    [os.remove(itm) for itm in loadimages(indir)
     if bname(itm) == 'output_retrieval_cimaq_3589314_1.text.txt']
    [os.rename(itm, join(dname(itm), bname(itm).split('.')[0]+splitext(bname(itm))[1]))
     for itm in loadimages(indir) if splitext(bname(itm))[0].endswith(splitext(bname(itm))[0])]

def main():
    cimaq_filter()
    
if __name__ == "__main__":
    main()
