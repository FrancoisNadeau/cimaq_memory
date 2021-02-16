#!/usr/bin/env python3

from cimaq_utils import *
from cimaq_utils import loadimages
from blind_rename import *
from inspect_misc_text import *
from zipctl import uzipfiles
from get_infos import get_infos
from os.path import expanduser as xpu
from collections import OrderedDict

def prep_sheet(filename, encoding, hdr, delimiter, width, lineterminator,
               dupindex, row_breaks, n_fields, n_lines, new_delim='\t'):
    rawsheet = open(filename , "rb", buffering=0)
    nsheet = []
    if dupindex:
        good = evenodd(tuple(tuple(no_ascii(line.decode(encoding)).lower(
                   ).encode('utf8').decode('utf8').split()[:row_breaks[-1]+1])
                             for line in rawsheet.readlines()))[0]
        good = df('\t'.join(itm.replace(' ', '_') for itm in line).split('\t')
                     for line in good).fillna(str(np.nan))
        rawsheet.seek(0)
        evelst, oddlst = evenodd(tuple(no_ascii(line.decode(encoding)).lower(
                                       ).encode('utf8').decode('utf8').replace(2*delimiter,
                                                           delimiter+str(np.nan)+delimiter).split()[row_breaks[-1]+1:]
                                  for line in rawsheet.readlines()))
        toclean = tuple(tuple(dict.fromkeys((flatten(itm))))
                        for itm in tuple(zip(evelst, oddlst)))
        toclean = df(tuple(flatten(item)) for item in toclean)
        ndf = []
        for row in toclean.iterrows():
            if row[1].isnull().any():
                ndf.append(['NON'] + row[1].values.tolist())
            else:
                ndf.append(row[1].values)
        toclean = pd.concat([good, df(ndf)], axis=1).dropna(axis=1, how='all').drop_duplicates()
    else:
        toclean = tuple(tuple(no_ascii(line.decode(encoding)).lower(
                      ).encode('utf8').decode('utf8').strip().replace(2*'\t',
                                                           '\t'+str(np.nan)+'\t').replace(' ', '_').split())
                          for line in rawsheet.readlines())
        for line in toclean:
            nline = tuple(itm for itm in line)
            nsheet.append(nline)
        toclean = tuple('\t'.join(no_ascii(itm).replace(' ', 'NON')
                                  for itm in flatten(line))
                        for line in nsheet)
        toclean = df((line.split('\t') for
                      line in toclean)).convert_dtypes('int').fillna('NON')
        toclean = df((row[1].values.tolist()
                      for row in toclean.iterrows())).dropna(axis=1, how='all').drop_duplicates()        
    rawsheet.close()
    if hdr:
        toclean = toclean.T.set_index(0).T.reset_index(drop=True)
    else:
        toclean = toclean.T.reset_index(drop=True).T
    toclean = toclean.fillna('NON').replace('NON', str(np.nan))
    return toclean.replace('nan', np.nan).dropna(axis=1, how='all')
    
def main():
    prep_sheet(filename, encoding, hdr, delimiter, width, lineterminator,
               dupindex, row_breaks, n_fields, n_lines, new_delim)

if __name__ == "__main__":
    main()    