#!/usr/bin/env python

import chardet
import os
from chardet import detect
from os.path import basename as bname
from get_encoding import get_encoding

def sniffsheet(indir="~/extracted_eprimeF"):
    indir = xpu(indir)
    p1 = pd.read_csv(join(indir, "participants.tsv"),
                     sep='\t').set_index("sub-ID")
    p1['encp'] = [get_encoding([os.path.join(indir, row[0], item)
                                 for item in ls(join(indir, row[0]))
                               if not bool(item.startswith("._") or
                                           os.path.isdir(join(indir,
                                                              row[0], item)))])
                  for row in p1.iterrows()]
    
    p1.to_csv(join(indir, "participants_decoder.tsv"), sep='\t')
    # List recurrent sting patterns in relatively homeneously named dataset
    prefixes = sorted(list(dict.fromkeys([bname(item).split("CIMAQ")[0] 
                for item in flatten([list(df(p1.to_dict()['encp'].values()))])
               if "CIMAQ" in bname(item)])))
    return p1, prefixes
