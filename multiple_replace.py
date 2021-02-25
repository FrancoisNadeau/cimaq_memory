#!/usr/bin/env python3

import re
from typing import Union

def multiple_replace(adict:dict, text:Union[str, bytes], encoding:str=None):
  # Create a regular expression  from the dictionary keys
    encoding = [encoding if encoding else 'utf8'][0]
    regex = re.compile("(%s)".encode(encoding) % \
                     "|".encode(encoding).join(map(re.escape, adict.keys())))
  # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: adict[mo.string[mo.start():mo.end()]], text) 

if __name__ == "__main__": 
    multiple_replace(adict, text)
#   text = "Larry Wall is the creator of Perl"

#   dict = {
#     "Larry Wall" : "Guido van Rossum",
#     "creator" : "Benevolent Dictator for Life",
#     "Perl" : "Python",
#   } 

#   return multiple_replace(dict, text)
