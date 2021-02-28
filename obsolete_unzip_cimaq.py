# #!/usr/bin/env python3

# from blind_rename import rename_imposter_cols

# from cimaq_utils import flatten
# from cimaq_utils import get_cimaq_dir_paths
# from cimaq_utils import loadfiles
# from cimaq_utils import loadimages
# from cimaq_utils import sortmap

# from inspect_misc_text import *
# from inspect_zip import *

# from zipctl import uzipfiles
# from zipctl import getnamelist
# from zipctl import getinfolist

# from chardet import UniversalDetector as udet
# from os.path import expanduser as xpu
# from os.path import join as pjoin
# from typing import Union
# from zipfile import ZipFile
# from tqdm import tqdm

# from removeEmptyFolders import removeEmptyFolders

# # 'cimaq_derivatives/task_files/uzeprimes'
# # cimaq_dir= '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives'

# def unzip_cimaq(cimaq_dir:Union[os.PathLike, str], keepinfos:bool=False, keepsheets:bool=False):
#     dlst, patterns = get_cimaq_dir_paths(cimaq_dir)[:2]  
#     zip_contents = [scan_zip_contents(fpath, exclude = ['pratique', 'practice', '.pdf', '.edat2'],
#                                    to_xtrct = [],
#                                    withbytes=True,
#                                    dst_path = dlst.uzeprimes.fpaths)
#                     for fpath in tqdm(loadimages(dlst.zeprimes.fpaths),
#                                       desc = 'scanning')]

#     sheet_infos = pd.concat([pd.concat([df(pd.Series({**scan_archv(row[1].bsheets),
#                                                       **row[1].to_dict()}))
#                                         for row in itm.iterrows()],
#                                        axis=1).T.reset_index(drop=True)
#                              for itm in tqdm(zip_contents, desc = 'sniffing')])

#     sheet_infos['newsheets'] = [df([line.split() for line in
#                                      mkfrombytes(row[1].bsheets, row[1].encoding,
#                                                  row[1].delimiter,
#                                                  row[1].has_header).splitlines()])
#                                  if not row[1].dup_index else
#                                  fix_dupindex(mkfrombytes(row[1].bsheets, row[1].encoding,
#                                                           row[1].delimiter,
#                                                           row[1].has_header))
#                                 for row in tqdm(sheet_infos.iterrows(), desc = 'repairing')]
    
#     sheet_infos = sheet_infos.drop([row[0] for row in sheet_infos.iterrows()
#                                     if row[1].newsheets.shape == (0, 0)], axis = 0)
    
#     newsheets = [('_'.join(itm for itm in pd.Series(row[1].filename.lower().replace('-', '_').split('_')).unique()),
#                   row[1].newsheets.T.reset_index(drop=True).T.convert_dtypes(float))
#                  if not row[1].has_header else
#                  ('_'.join(pd.Series([str(itm) for itm in
#                                       row[1].filename.lower().replace('-', '_').split('_')]).unique()),
#                   row[1].newsheets.T.set_index(0).T.convert_dtypes(float))
#                  for row in tqdm(sheet_infos.iterrows(), desc = 'headers')]
#     [itm[1].to_csv(pjoin(dlst.uzeprimes.fpaths,
#                          os.path.splitext(itm[0])[0]+'.tsv'),
#                    index=False, sep='\t') for itm in tqdm(newsheets, desc = 'saving')]
    
#     if keepinfos and not keepsheets:
#         return sheet_infos.drop(columns = ['bsheets', 'newsheets'])
#     if keepsheets and not keepinfos:
#         return sorted(newsheets)
#     if keepsheets and keepinfos:
#         return tuple(zip([row[1] for row in
#                           sheet_infos.drop(columns = ['bsheets',
#                                                       'newsheets']).sort_values(
#                               'filename').iterrows()],
#                          sorted(newsheets)))

# def main():
#     unzip_cimaq(cimaq_dir)

# if __name__ == "__main__":
#     main()
