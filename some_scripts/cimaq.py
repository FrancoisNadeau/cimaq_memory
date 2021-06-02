#! /usr/bin/env python

import os
from typing import Union
from fetch_cimaq import fetch_cimaq

class cimaq:
    @ classmethod
    def fetch(self, cimaq_dir: Union[str, os.PathLike]):
        return fetch_cimaq(cimaq_dir)

def main():
    return cimaq.fetch(cimaq_dir)
 
if __name__ == "__main__":
    main()
