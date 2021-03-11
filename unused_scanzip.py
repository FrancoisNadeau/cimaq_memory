# #! /usr/bin/env python

# import os
# import pandas as pd

# import sniffbytes as snif

# from os.path import basename as bname
# from os.path import dirname as dname
# from os.path import join as pjoin
# from pandas import DataFrame as df
# from tqdm import tqdm
# from typing import Union
# from zipfile import ZipFile

# from sniffbytes import filter_lst_exc
# from sniffbytes import filter_lst_inc

# from sniffbytes import evenodd

# def scansniff_zip(
#     archv_path: Union[str, os.PathLike],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     to_xtrct: Union[str, list, tuple] = [],
#     dst_path: Union[str, os.PathLike] = None
# ) -> object:
#     scanned_zip = [scanzip(fpath, ntpl,to_xtrct=[], exclude,
#                            to_xtrct, dst_path, withbytes=True)
#                    for fpath in tqdm(filter_lst_exc(
#                        exclude, sorted(snif.loadimages(archv_path))),
#                                      desc="scanning")]
#     zip_contents = [df(pd.concat([row[1], pd.Series(snif.scan_bytes(row[1]["bsheets"]),
#                                                     dtype = object)])
#                        for row in itm.sort_values("filename").iterrows())
#                     for itm in tqdm(scanned_zip, desc="sniffing")]
#     return zip_contents

# def get_zip_contents(
#     archv_path: Union[os.PathLike, str],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     to_xtrct: Union[str, list, tuple] = [],
#     to_close: bool = True,
#     withbytes: bool = False,
#     to_sniff: bool = False
# ) -> object:
#     myzip = ZipFile(archv_path)
#     ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

#     vals = (
#         df(
#             tuple(
#                 dict(zip(snif.evenodd(itm)[0], snif.evenodd(itm)[1]))
#                 for itm in tuple(
#                     tuple(snif.force_ascii(repr(
#                         itm.lower())).strip().replace("'", "")
#                         .replace("'", "")
#                         .replace("=", " ")[:-2]
#                         .split()
#                     )[1:]
#                     for itm in set(
#                         repr(myzip.getinfo(itm))
#                         .strip(" ")
#                         .replace(itm, itm.replace(" ", "_"))
#                         if " " in itm
#                         else repr(myzip.getinfo(itm)).strip(" ")
#                         for itm in ntpl
#                     )
#                 )
#             ),
#             dtype="object",
#         )
#         .sort_values("filename")
#         .reset_index(drop=True)
#     )
#     vals[["src_name", "ext"]] = [(nm, os.path.splitext(nm)[1]) for nm in ntpl]
#     vals["filename"] = [
#         "_".join(
#             pd.Series(
#                 row[1].filename.lower().replace("/",
#                                                 "_").replace("-",
#                                                              "_").split("_")
#             ).unique()
#             .__iter__()
#         )
#         for row in vals.iterrows()
#     ]
#     if exclude:
#         vals = vals.drop(
#             [row[0] for row in vals.iterrows() if row[1].filename
#              not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
#             ],
#             axis=0,
#         )
#     if withbytes:
#         vals["bsheets"] = [
# #             snif.strip_null() 
#             myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
#         ]
#     if to_sniff:
#         vals[["encoding", "delimiter", "has_header", "width", "dup_index", "nrows"]] = \
#             [tuple(snif.scan_bytes(row[1].bsheets).values()) for row in vals.iterrows()]
#     if to_close:
#         myzip.close()
#         return vals
#     else:
#         return (myzip, vals)

# def get_zip_contents(
#     archv_path: Union[os.PathLike, str],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     withbytes: bool = False,
#     to_sniff: bool = False,
#     to_close: bool = True,
# ) -> object:
#     myzip = ZipFile(archv_path)
#     ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

#     vals = (
#         df(
#             tuple(
#                 dict(zip(evenodd(itm)[0], evenodd(itm)[1]))
#                 for itm in tuple(
#                     tuple(
#                         force_ascii(repr(itm.lower()))
#                         .strip()
#                         .replace("'", "")
#                         .replace("'", "")
#                         .replace("=", " ")[:-2]
#                         .split()
#                     )[1:]
#                     for itm in set(
#                         repr(myzip.getinfo(itm))
#                         .strip(" ")
#                         .replace(itm, itm.replace(" ", "_"))
#                         if " " in itm
#                         else repr(myzip.getinfo(itm)).strip(" ")
#                         for itm in ntpl
#                     )
#                 )
#             ),
#             dtype="object",
#         )
#         .sort_values("filename")
#         .reset_index(drop=True)
#     )
#     vals[["src_name", "ext"]] = [(nm, os.path.splitext(nm)[1]) for nm in ntpl]
#     vals["filename"] = [
#         "_".join(
#             pd.Series(
#                 row[1].filename.lower().replace("/",
#                                                 "_").replace("-",
#                                                              "_").split("_")
#             ).unique()
#             .__iter__()
#         )
#         for row in vals.iterrows()
#     ]
#     if exclude:
#         vals = vals.drop(
#             [
#                 row[0]
#                 for row in vals.iterrows()
#                 if row[1].filename
#                 not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
#             ],
#             axis=0,
#         )

#     if withbytes:
#         vals["bsheets"] = [
# #             snif.strip_null() 
#             myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
#         ]
        
#     if to_sniff:
#         vals[["encoding", "delimiter", "has_header", "width", "dup_index", "nrows"]] = \
#             [tuple(snif.scan_bytes(row[1].bsheets).values()) for row in vals.iterrows()]
#     if to_close:
#         myzip.close()
#         return vals
#     else:
#         return (myzip, vals)

# def main():    
#     if __name__ == "__main__":
#         scan_zip(archv_path, ntpl, exclude, to_xtrct, dst_path)
