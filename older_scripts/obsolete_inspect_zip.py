# #!/usr/bin/env python3

# # import chardet
# import os
# import pandas as pd
# import regex as re
# import shutil

# from os.path import basename as bname
# from os.path import dirname as dname
# from os.path import join as pjoin
# from pandas import DataFrame as df
# from tqdm import tqdm
# from typing import Union
# from zipfile import ZipFile

# from removeEmptyFolders import removeEmptyFolders

# from cimaq_utils import loadfiles
# from cimaq_utils import loadimages
# from inspect_misc_text import evenodd
# from inspect_misc_text import filter_lst_exc
# from inspect_misc_text import filter_lst_inc
# from inspect_misc_text import filter_lst_inc
# from inspect_misc_text import no_ascii
# from sniffbytes import scan_bytes

# def getnametuple(myzip): 
#     '''
#     Adjustment to ZipFile.namelist() function to prevent MAC-exclusive
#     '__MACOSX' and '.DS_Store' files from interfering.
#     Only necessary for files compressed with OS 10.3 or earlier.
#     Source: https://superuser.com/questions/104500/what-is-macosx-folder
#     Command line solution:
#         ``` zip -r dir.zip . -x ".*" -x "__MACOSX"
#     Source: https://apple.stackexchange.com/questions/239578/compress-without-ds-store-and-macosx
#     '''
#     return tuple(sorted(list(itm for itm in
#                              myzip.namelist()
#                              if  bname(itm).startswith('.') == False \
#                              and '__MACOSX' not in itm \
#                              and 'textClipping' not in itm
#                              and itm != os.path.splitext(bname(dname(itm)))[0]+'/')))

# def get_zip_contents(archv_path:Union[os.PathLike, str],
#                      ntpl:Union[str, list, tuple]=[],
#                      exclude:Union[str, list, tuple]=[],
#                      to_close:bool=True)->object:
#     myzip = ZipFile(archv_path)
#     ntpl = [ntpl if ntpl else getnametuple(myzip)][0]
    
#     vals = df(tuple(dict(zip(evenodd(itm)[0], evenodd(itm)[1])) for itm
#                     in tuple(tuple(no_ascii(repr(itm.lower())).strip().replace(
#                "'", "").replace("'",'').replace(
#                    '=',' ')[:-2].split())[1:]
#                for itm in set(repr(myzip.getinfo(itm)).strip(
#                    ' ').replace(itm, itm.replace(' ', '_')) if ' ' in
#                        itm else repr(myzip.getinfo(itm)).strip(
#                            ' ') for itm in ntpl))), dtype='object').sort_values(
#                                'filename').reset_index(drop=True)
#     vals[['src_name', 'ext']] = [(nm, os.path.splitext(nm)[1])
#                                     for nm in ntpl]
#     vals['filename'] = ['_'.join(pd.Series(row[1].filename.replace(
#                            '/', '_').replace('-', '_').lower().split(
#                                '_')).unique().__iter__())
#                         for row in vals.iterrows()]
#     if exclude:
#         vals = vals.drop([row[0] for row in vals.iterrows()
#                           if row[1].filename not in filter_lst_exc(
#                               exclude, [itm.lower() for itm in vals.filename])], axis=0)    
#     if to_close:
#         myzip.close()
#         return vals
#     else:
#         return (myzip, vals)

# def scan_zip_contents(archv_path:Union[os.PathLike, str],
#                       ntpl:Union[str, list, tuple]=[],
#                       to_xtrct:Union[str, list, tuple]=[],
#                       exclude:Union[str, list, tuple]=[],
#                       to_close:bool=True, withbytes:bool=False,
#                       dst_path: Union[os.PathLike, str]=None)->object:
    
#     myzip, vals = get_zip_contents(archv_path, ntpl,
#                                    exclude, to_close=False)
#     if exclude:
#         vals = vals.drop([row[0] for row in vals.iterrows()
#                           if row[1].filename not in filter_lst_exc(
#                               exclude, [itm.lower() for itm in vals.filename])], axis=0)
#     if to_xtrct:
#         dst_path = [dst_path if dst_path
#                     else pjoin(dname(archv_path),
#                                os.path.splitext(bname(archv_path))[0])][0]
#         os.makedirs(dst_path, exist_ok = True)
#         xtrct_lst = vals.loc[[row[0] for row in vals.iterrows()
#                               if row[1].filename in
#                               filter_lst_inc(to_xtrct,
#                                              list(vals.filename),
#                                             sort=True)]]
#         [shutil.move(myzip.extract(member=row[1].src_name,
#                                    path=dst_path),
#                      pjoin(dst_path, '_'.join(pd.Series(row[1].filename.lower().replace(
#                          '-', '_').split('_')).unique())))
#          for row in tqdm(xtrct_lst.iterrows(), desc = 'extracting')]
#         vals = vals.loc[[row[0] for row in vals.iterrows()
#                          if row[1].filename not in xtrct_lst.values]]
#         removeEmptyFolders(dst_path, False)
#     if withbytes:
#         vals['bsheets'] = [myzip.open(row[1].src_name).read().lower()
#                            for row in vals.iterrows()]
#     if to_close:
#         myzip.close()
#     return vals.reset_index(drop = True)

# def scansniff_zip(folderpath:Union[str, os.PathLike],
#                   exclude:Union[str, list, tuple]=[]):
#     scanned_zip = [scan_zip_contents(fpath, to_xtrct=[], exclude=exclude, withbytes=True)
#                    for fpath in tqdm(sorted(loadimages(folderpath)),
#                                       desc = 'scanning')]
#     zip_contents = [df(pd.concat([row[1], pd.Series(scan_bytes(row[1]['bsheets']))])
#                      for row in itm.sort_values('filename').iterrows())
#                     for itm in tqdm(scanned_zip, desc = 'sniffing')]
#     return zip_contents




