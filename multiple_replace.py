#!/usr/bin/env python3

import regex as re
from typing import Union

def multiple_replace(adict:dict, text:Union[str, bytes], encoding:str=None):
    """ Adapted from source:
        https://code.activestate.com/recipes/81330-single-pass-multiple-replace/
    """
  # Create a regular expression  from the dictionary keys
    adict = dict((itm[0].encode(), itm[1].encode())
                 for itm in new.items())
    encoding = [encoding if encoding else 'UTF-8'][0]
    regex_pattern = re.compile("(%s)".encode(encoding) % \
                     "|".encode(encoding).join(map(re.escape,
                     adict.keys())))
  # For each match, look-up corresponding value in dictionary
    mo = b"mo"
    return (adict, regex_pattern,
            regex_pattern.sub(lambda mo: \
                              adict[mo.string[mo.start():mo.end()]],
                              text.encode()).decode())

if __name__ == "__main__": 
    multiple_replace(adict, text.encode())
