#!/usr/bin/env python3

# import chardet
# import collections
# import csv
# import glob
# import io
# import itertools
# import json
# import numpy as np
# import os
# import pandas as pd
# import random
# import re
# import reprlib
# import shutil
# import string
# import sys

# from chardet import detect
# from chardet.universaldetector import UniversalDetector as udet
# from collections import Counter
# from collections import OrderedDict
# from functools import reduce
# from io import StringIO
# from matplotlib import pyplot as plt
# from numpy import nan as NaN
# from operator import itemgetter 
# from os import getcwd as cwd
# from os import listdir as ls
# from os.path import basename as bname
# from os.path import dirname as dname
# from os.path import expanduser as xpu
# from os.path import join
# from os.path import splitext
# from pandas import DataFrame as df
# from tqdm import tqdm
# from typing import Sequence
# from removeEmptyFolders import removeEmptyFolders

####################################
############## Unused ##############
'
# def absoluteFilePaths(maindir):
#     for allthings in os.walk(maindir):
#         for folder in allthings[1]:
#             yield os.path.abspath(os.path.join(dirpath, f))

# def prepms(sheetnames):
#     for sheet in sheetnames['sheetvalues']:
#         if 'participant_id' in list(sheet.columns):
#             sheet = sheet.rename(columns={'participant_id': 'dccid'})
#         if 'id' in list(sheet.columns):
#             sheet = sheet.rename(columns={'id': 'dccid'})        
#         if 'dccid' in list(sheet.columns):
#             sheet['dccid'] = sheet['dccid']
#         if 'sub_ids' in list(sheet.columns):
#             sheet = sheet.rename(columns={'sub_ids': 'dccid'})        
#         sheet.columns = map(str.lower, sheet.columns)
#         sheet.columns = map(str.strip, sheet.columns)        
# #         sheet = sheet.set_index(list(sheet.columns)[0]).sort_index()
#         sheet = sheet.reindex(sorted(sheet.columns), axis=1).dropna()
#     return sheetnames

# def mkvsheet(sheetnames):
#     meansheets = [sheet for sheet in
#                   sheetnames['sheetvalues']]
#     l1 = [sheet.dropna() for sheet in meansheets
#           if 'dccid' in list(sheet.columns)]
#     l2 = [sheet.dropna() for sheet in meansheets
#           if 'pscid' in list(sheet.columns)]
#     l1df = megamerge(l1, 'outer', onto='dccid')
#     l2df = megamerge(l2, 'outer', onto='dccid') 
#     l3df = pd.merge(l1df, l2df, how='outer',
#                     left_on='pscid_y', right_on='pscid_y')
#     colsorder = pd.Series(l3df.columns)
#     l3df = l3df.T.drop_duplicates(keep='first').T
#     ncols = [col.replace('_x', '')
#              for col in l3df.columns
#               if '_x' or '_y' in col]
#     l3df.columns = ncols
#     l3df = l3df.dropna()
#     l3df['dccid'] = [int(str(itm).split('.')[0]) for itm in l3df.dccid]
#     l3df['pscid'] = [int(str(itm).split('.')[0]) for itm in l3df.pscid]
#     l3df.to_csv(join(cimaq_dir, 'task_files',
#                      'mean_vectors.tsv'), sep='\t')
#     return l3df

# def mkmeansheet(indir= '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants',
#                 snames = ['Neuropsych/ALL_Neuropsych_scores.tsv',
#                              'MotionResults/fMRI_meanMotion.tsv',
#                              'TaskResults/fMRI_behavMemoScores.tsv',
#                              'MemoTaskParticipantFile.tsv',
#                              'Participants_bids.tsv',
#                              'Splitting_list.tsv']):

#     meansheet = mkvsheet(prepms(loadsheets(snames,
#                                            xpu(indir)).dropna()))
#     meansheet['pscid'] = [str(itm).split('.')[0]
#                           for itm in meansheet.pscid]
#     meansheet['dccid'] = [str(itm).split('.')[0]
#                           for itm in meansheet.dccid]
#     qcok = pd.read_csv(join(indir, 'sub_list_TaskQC.tsv'),
#                        sep='\t').values.tolist()
#     qcok = [ind for ind in qcok if ind in list(meansheet.dccid)]
#     meansheet = meansheet.loc[[meansheet.dccid in qcok]]
#     return meansheet.drop(columns=['pscid_y'])

# def prep_sheet(filename, encoding, hdr, delimiter, width, lineterminator,
#                dupindex, row_breaks, n_fields, n_lines, new_delim='\t'):
#     rawsheet = open(filename , "rb", buffering=0)
#     nsheet = []
#     if dupindex:
#         good = evenodd(tuple(tuple(no_ascii(line.decode(encoding)).lower(
#                    ).split()[:row_breaks[-1]+1])
#                              for line in rawsheet.readlines()))[0]
#         good = tuple('\t'.join(itm.replace(' ', '_') for itm in line)
#                      for line in good)
#         rawsheet.seek(0)
#         evelst, oddlst = evenodd(tuple(no_ascii(line.decode(encoding)).lower(
#                                        ).split()[row_breaks[-1]+1:]
#                                   for line in rawsheet.readlines()))
#         toclean = tuple(tuple(dict.fromkeys((flatten(itm))))
#                         for itm in tuple(zip(evelst, oddlst)))
#         for line in toclean:
#             if len(line) < n_fields+1:
#                 nline = 'n\a'+'\t'  + '\t'.join(itm.replace(' ', '_') for itm in line)
#             else:
#                 nline = '\t'.join(itm.replace(' ', '_') for itm in line)
#             nsheet.append(nline)
#         toclean = tuple(zip(tuple(line.split('\t')
#                                   for line in good),
#                             tuple(line.split('\t')
#                                   for line in nsheet)))
#         toclean = tuple('\t'.join(itm for itm in flatten(line))
#                         for line in toclean)
#     else:
#         toclean = tuple(no_ascii(line.decode(encoding)).lower().split()
#                         for line in rawsheet.readlines())
#         for line in toclean:
#             nline = tuple(itm.replace(' ', '_') for itm in line)
#             nsheet.append(nline)
#         toclean = tuple('\t'.join(itm for itm in flatten(line))+'\n'
#                             for line in toclean)
#     rawsheet.close()
#     return toclean

# def fixbrokensheet(inpt):
#     inpt = df(inpt)
#     eve, odd = evenodd_col(inpt)
#     cnames = dupcols(df(inpt)).columns
#     # Both doubles_even & doubles_odd are the same
#     doubles_even = df(eve, dtype='object')[[itm[1] for itm in cnames if itm[0]]]
#     doubles_odd = df(odd, dtype='object')[[itm[1] for itm in cnames if itm[0]]]
#     singles_even = df(eve, dtype='object')[[itm[1] for itm in cnames if not itm[0]]]
#     singles_odd = df(odd, dtype='object')[[itm[1] for itm in cnames if not itm[0]]]
#     rescued = pd.concat([singles_even.dropna(axis=0),
#                          singles_odd.dropna(axis=0)],
#                         axis=1).T.drop_duplicates()
#     final = pd.concat([doubles_even, rescued], axis=1)


# def emptydir(folder = '/path/to/folder'):
#     for filename in os.listdir(folder):
#         file_path = os.path.join(folder, filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path)
#             elif os.path.isdir(file_path):
#                 shutil.rmtree(file_path)
#         except Exception as e:
#             print('Failed to delete %s. Reason: %s' % (file_path, e))

############################
######### Broken ###########

# def get_meansheet(sdir='/media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants'):
#     snames = ['Participants_bids.tsv',
#               'MemoTaskParticipantFile.tsv',
#               'TaskResults/fMRI_behavMemoScores.tsv',
#               'Neuropsych/ALL_Neuropsych_scores.tsv',
#               'MotionResults/fMRI_meanMotion.tsv',
#               'sub_list_TaskQC.tsv']
#     constant_dir = xpu('~/../..')
#     spaths = [join(constant_dir, sdir, sname)
#               for sname in snames]
#     encs = [get_encoding(spath) for spath in spaths]
#     infos = df(tuple(zip(spaths, encs)))
#     sheets = [pd.read_csv(row[1][0], encoding=row[1][1], sep='\t')
#               for row in infos.iterrows()]
#     allvals = [list(enumerate([itm[1].sort_values() for itm in sheet.iteritems()]))
#                for sheet in sheets]
#     test = tuple(enumerate(tuple(itertools.chain.from_iterable(allvals))))
#     allcols = pd.Series([itm[1][1][0] for itm in test])
#     valsonly = [(itm[0], itm[1][1][1][1]) for itm in enumerate(test)]
#     uvals = df([itm for itm in enumerate(valsonly)]).drop_duplicates().T
#     colnames = allcols.loc[uvals.columns].to_dict()
#     uvals = uvals.rename(columns=colnames)
#     uvals = uvals.loc[sheets[-1].index]
#     uvals.columns = map(str.lower, uvals.columns)
#     return uvals

# uvals = get_meansheet().convert_dtypes().drop_duplicates().T

# def splitmerge(inpt):
#     evlst, odlst = evenodd([itm[0] for itm in inpt])
#     evvals = itemgetter(*[itm[0] for itm in
#                           enumerate(evlst)])(inpt)
#     odvals = itemgetter(*[itm[0] for itm in
#                           enumerate(odlst)])(inpt)
# #     evelst, oddlst = Split([line[0] for line in inpt])
#     hdr = bytearray(str(inpt[0]), 'utf8').decode() not in '.-0123456789'
#     cnames=None
#     if hdr == True:
# #         hdr = 0
# #         evlst, odlst = evlst[1:], odlst[1:]
#         evvals, odvals = evvals[1:], odvals[1:]
# #         cnames = pd.Series(evvals[0] + odvals[0]).unique().tolist()
#         cnames = evvals[0]
#     else: evvals, odvals, cnames = evvals, odvals, cnames 
#     if evlst == odlst:
#         try:
#             evdfl = df(enumerate(evvals), columns=cnames).drop_duplicates(keep='last')
#             evdfn = df(enumerate(evvals), columns=cnames).drop_duplicates(keep=False)
# #             oddff = df(odvals, columns=cnames).drop_duplicates(keep='first')
#             oddfl = df(enumerate(odvals), columns=cnames).drop_duplicates(keep='last')
#             oddfn = df(enumerate(odvals), columns=cnames).drop_duplicates(keep=False)
#             outpt = megamerge([evdfl, evdfn, oddfl, oddfn], howto='outer', onto=cnames)
#         except ValueError:
            
#             outpt = df(inpt).pad()
# #             outpt =  df(enumerate([[''.join([itm for itm in line
# #                                     if ' ' not in itm]).strip('\n').replace('nnn', ',').replace('nn', ',')]
# #                          for line in inpt]))
# #         return evdf, oddf
# #         return megamerge([evdff, oddfl, evdfl, oddff], howto='outer', onto=cnames)
# #         df1 = pd.merge(evdf, oddf)
# #         return df1
# #         df2 = pd.merge(evdf, oddf).drop_duplicates(keep='last')
# #         return pd.merge(df1, df2, on=0, sort=True)
#     else:
# #         outpt = pd.read_fwf(np.array(inpt), header=None)
#         outpt = df(inpt)
# #         outpt = df(pd.Series(enumerate(inpt)).unique()).dropna(axis=1, how='all')
#     return outpt

# def prepstr(filename, encoding, hdr, sep):
#     sheet = open(filename , "r", encoding=encoding)
# #     if sep != '\t':
# #         nsep = '\t'
#     sep = csv.Sniffer().sniff(sheet.readline()).delimiter    
#     test = []
#     test2 = []
#     test3 = []
# #     widths = []
#     widths = []
# #     hdr = bytearray(str(sheet[0]), 'utf8').decode() not in '.-0123456789'

#     nitems = []
#     for line in sheet.readlines():
#         line = no_ascii(line)
# #         line = line.replace('    ', ' ')
# #         line = line.replace(' . ', ' n\a ')
# #         line = line.lstrip()
# #         line = line.rstrip()
# #         line = line.strip('    ')
# #         line = line.replace('    ', ' ')
#         line = line.strip().replace(sep, '\t').replace(' ', '_')
# #         line = no_ascii(line)
#         widths.append(len(line.encode(encoding)))
#         line = line.ljust(len(line)).strip()
#         line = line.rjust(len(line)).strip()
# #         line = line.strip('n')
#         line = line.split()
#         line2 = sep.join(itm for itm in line).strip().lstrip().rstrip()
# #         line2 = line.ljust(len(line)).strip()
# #         line2 = line.rjust(len(line)).strip()        
#         test.append(line)
#         line2 = line2.strip().split()
#         test2.append(line2)
#         line3 = line2.strip()
#         nitems.append(len(line2))
#     nitems = pd.Series(nitems).max()
#     nrows = len(test2)
#     maxwidth = pd.Series(widths).max
#     if hdr:
#         width = pd.Series(widths[1:]).max()
#         nitems = pd.Series(nitems[1:]).max()
#         test = [line[:width] for line in test[1:]]
#         colnames = test2[0][:nitems]
#         nrows = len(test2[1:])
    

# #         test = [line[:width] for line in test]
# #         ncol.append(line.count(sep))
#     test2 = [line[:nitems] for line in test2]

#     sheet.close()
#     return test3

# def prepbytes(filename, encoding, hdr, sep):
#     sheet = open(filename , "r", encoding=encoding)
# #     if sep != '\t':
# #         nsep = '\t'
# #     sep = csv.Sniffer().sniff(sheet.readline()).delimiter    
#     test = []
#     test2 = []
# #     widths = []
#     widths = []
# #     hdr = bytearray(str(sheet[0]), 'utf8').decode() not in '.-0123456789'
#     nitems = []
#     for line in sheet.readlines():
#         line = no_ascii(line)
# #         line = line.replace('    ', ' ')
# #         line = line.replace(' . ', ' n\a ')
# #         line = line.lstrip()
# #         line = line.rstrip()
# #         line = line.strip('    ')
# #         line = line.replace('    ', ' ')
#         line = line.strip().replace(sep, '\t').replace(' ', '_')
# #         line = no_ascii(line)
#         widths.append(len(line.encode(encoding)))
#         line = line.ljust(len(line)).strip()
#         line = line.rjust(len(line)).strip()
# #         line = line.strip('n')
#         line = line.split()
#         line2 = sep.join(itm for itm in line).strip().lstrip().rstrip()
# #         line2 = line.ljust(len(line)).strip()
# #         line2 = line.rjust(len(line)).strip()        
#         test.append(line)
#         line2 = line2.strip().split()
#         test2.append(line2)
#         nitems.append(len(line2))
#     nitems = pd.Series(nitems).max()
#     nrows = len(test2)
#     maxwidth = pd.Series(widths).max
#     if hdr:
#         width = pd.Series(widths[1:]).max()
#         nitems = pd.Series(nitems[1:]).max()
#         test = [line[:width] for line in test[1:]]
#         colnames = test2[0][:nitems]
#         nrows = len(test2[1:])

# def evenodd_col(inpt):
# #     inpt = [line[0] for line in inpt]
#     evlst, odlst = evenodd([itm[0] for itm in enumerate(inpt)])
#     evvals, odvals = listat(evlst, inpt), listat(odlst, inpt)
#     return df(itemgetter(*evlst)(inpt)), df(itemgetter(*odlst)(inpt))

# def get_singlerows2(inpt):
#     rowbreaks = [item[0] for item
#                  in enumerate(inpt.iteritems())
#                  if not splitrows2(item[1][1])]
#     return inpt[tuple(itemgetter(*rowbreaks)(tuple(inpt.columns)))]

#     evlst, odlst = oddeven([itm[0] for itm in enumerate(inpt)])
#     evvals = itemgetter(*evlst)(inpt)
#     odvals = itemgetter(*odlst)(inpt)
#     return bool(pd.Series(evvals).values == pd.Series(odvals).values)

