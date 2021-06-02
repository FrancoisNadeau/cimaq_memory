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

def get_dst_path(
    src_path: Union[str, os.PathLike] = "",
    dst_path: Union[str, os.PathLike] = None
) -> str:
    return [xpu(dst_path) if dst_path
            else dname(xpu(src_path))][0]

def getallfiles(
    src_path: Union[str, os.PathLike]
) -> list:
    return loadfiles(sorted(loadimages(xpu(
        src_path)))).fpaths.values.tolist()

def to_tarxz(
    src_path: Union[str, os.PathLike],
    dst_path: Union[str, os.PathLike] = None
) -> None:
    with tarfile.open(pjoin(dname(
        get_dst_path(src_path, dst_path)),
                            bname(xpu(src_path))) + \
                      ".tar.xz", "w|xz") as nlst:
        for apath in tqdm(getallfiles(src_path),
                          desc = 'compressing'):
            with open(apath, "rb", buffering = 0) as afile:
                nlst.add(tarfile.TarInfo.frombuff(afile.read()))
            afile.close()
    nlst.close()

def main():
    ''' Creates .tar.xz archive'''
    if __name__ == "__main__":
        to_tarxz(src_path, dst_path)
