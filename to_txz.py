#!/usr/bin/env python3

import os
import tarfile
from os.path import basename as bname
from os.path import dirname as dname
from os.path import join as pjoin
from os.path import expanduser as xpu
from tqdm import tqdm
from typing import Union
from sniffbytes import loadfiles
from sniffbytes import loadimages

def get_file_list(src_path: Union[str, os.PathLike],
                  dst_path: Union[str, os.PathLike] = None) -> None:
    with open(get_dst_path(dst_path), 'wb') as newfile:
        newfile.write(b'\n'.join([b'\t'.join(itm.encode() for itm in
                                  sorted((loadimages(xpu(src_path)))))]))

def get_dst_path(src_path: Union[str, os.PathLike],
                 dst_path: Union[str, os.PathLike] = None) -> str:
    return [xpu(dst_path) if dst_path else dname(xpu(src_path))][0]

# def to_tarxz(src_path: Union[str, os.PathLike]):
#     with tarfile.open(pjoin(bname(xpu(src_path))) \
#                       + "_pathlist.tar.xz", "w|xz") as nlst:
#         [nlst.add(tarfile.TarInfo(apath)) for apath in
#          tqdm(loadfiles(sorted(loadimages(
#              xpu(src_path)))).fpaths.values.tolist(),
#               desc = 'compress')]
#     nlst.close()

def to_tarxz(
    src_path: Union[str, os.PathLike],
    dst_path: Union[str, os.PathLike] = None
) -> None:
    with tarfile.open(pjoin(dname(get_dst_path(src_path, dst_path),
                                  bname(xpu(src_path))) \
                      + ".tar.xz", "w|xz") as nlst:
        with open(apath, "rb", buffering = 0) as afile:
                      [nlst.add(tarfile.TarInfo(apath)) for apath in
         tqdm(loadfiles(sorted(loadimages(
             xpu(src_path)))).fpaths.values.tolist(),
              desc = 'compressing')]
    nlst.close()


def main():
    ''' Creates .tgz archive'''
    to_tarxz(src_path = "~/Desktop/cimaq2021/dcmfiles/all_dicom_images")

if __name__ == "__main__":
    main()

