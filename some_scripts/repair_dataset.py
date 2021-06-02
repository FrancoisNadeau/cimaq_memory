#! /usr/bin/env python

import os
import pandas as pd

import sniffbytes as snif

from os.path import basename as bname
from os.path import dirname as dname
from pandas import DataFrame as df
from typing import Union

def repair_dataset(
    folderpath: Union[str, os.PathLike],
    dst_path: Union[str, os.PathLike] = None,
    exclude: Union[str, list, tuple] = [],
) -> None:
    sctest = pd.concat(
        [
            itm.drop(
                [row[0] for row in itm.iterrows() if "empty_datas" in row[1].values],
                axis=0,
            )
            for itm in scansniff_zip(folderpath, exclude)
        ],
        ignore_index=True,
    ).sort_values("filename")

    sctest[["newsheets", "dst_path"]] = [
        itm[1]
        for itm in sorted(
            [
                (
                    row[1].filename,
                    (
                        snif.mkfrombytes(
                            row[1].bsheets,
                            row[1].encoding,
                            row[1].delimiter,
                            row[1].dup_index,
                        )
                        if not row[1].dup_index
                        else snif.fix_dupindex(
                            mkfrombytes(
                                row[1].bsheets,
                                row[1].encoding,
                                row[1].delimiter,
                                row[1].dup_index,
                            ),
                            row[1].has_header,
                            row[1].delimiter,
                        ),
                        pjoin(
                            [dst_path if dst_path else folderpath][0],
                            os.path.splitext(row[1].filename)[0] + ".tsv",
                        ),
                    ),
                )
                for row in tqdm(sctest.iterrows(), desc="repairing")
            ]
        )
    ]

    [
        snif.stream2file(row[1].newsheets, row[1].dst_path)
        for row in tqdm(sctest.iterrows(), desc="saving")
    ]

def main():    
    if __name__ == "__main__":
        repair_dataset(folderpath, dst_path, exclude)
        
# def repair_dataset(
#     folderpath: Union[str, os.PathLike],
#     dst_path: Union[str, os.PathLike] = None,
#     exclude: Union[str, list, tuple] = [],
# ) -> None:
#     sctest = pd.concat(
#         [
#             itm.drop(
#                 [row[0] for row in itm.iterrows() if "empty_datas" in row[1].values],
#                 axis=0,
#             )
#             for itm in scansniff_zip(folderpath, exclude)
#         ],
#         ignore_index=True,
#     ).sort_values("filename")

#     sctest[["newsheets", "dst_path"]] = [
#         itm[1]
#         for itm in sorted(
#             [
#                 (
#                     row[1].filename,
#                     (
#                         mkfrombytes(
#                             row[1].bsheets,
#                             row[1].encoding,
#                             row[1].delimiter,
#                             row[1].dup_index,
#                         )
#                         if not row[1].dup_index
#                         else fix_dupindex(
#                             mkfrombytes(
#                                 row[1].bsheets,
#                                 row[1].encoding,
#                                 row[1].delimiter,
#                                 row[1].dup_index,
#                             ),
#                             row[1].has_header,
#                             row[1].delimiter,
#                         ),
#                         pjoin(
#                             [dst_path if dst_path else folderpath][0],
#                             os.path.splitext(row[1].filename)[0] + ".tsv",
#                         ),
#                     ),
#                 )
#                 for row in tqdm(sctest.iterrows(), desc="repairing")
#             ]
#         )
#     ]

#     [
#         stream2file(row[1].newsheets, row[1].dst_path)
#         for row in tqdm(sctest.iterrows(), desc="saving")
#     ]

###################### BETTER LOOKING VERSION #######################################

# def repair_dataset(folderpath:Union[str, os.PathLike],
#                    dst_path:Union[str, os.PathLike]=None,
#                    exclude:Union[str, list, tuple]=[])->None:
#     sctest = pd.concat([itm.drop([row[0] for row in itm.iterrows()
#                         if 'empty_datas' in row[1].values],
#                        axis=0) for itm in
#               scansniff_zip(folderpath, exclude)],
#                        ignore_index=True).sort_values('filename')

#     sctest[['newsheets', 'dst_path']] = \
#         [(mkfrombytes(row[1].bsheets, row[1].encoding,
#                       row[1].delimiter, row[1].dup_index)
#                       if not row[1].dup_index else
#                       fix_dupindex(mkfrombytes(row[1].bsheets, row[1].encoding,
#                                                row[1].delimiter, row[1].dup_index),
#                                    row[1].has_header, row[1].delimiter),
#                       pjoin([dst_path if dst_path else folderpath][0],
#                             os.path.splitext(row[1].filename)[0]+'.tsv'))
#                      for row in tqdm(sctest.iterrows(), desc = 'repairing')]

#     [stream2file(row[1].newsheets, row[1].dst_path)
#      for row in tqdm(sctest.iterrows(), desc = 'saving')]

