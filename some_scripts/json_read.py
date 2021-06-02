#!/usr/bin/env python3

import json
import os
from typing import Union

def json_read(fp: Union[os.PathLike, str], mode: str, cls=None, object_hook=None, parse_float=None,
              parse_int=None, object_pairs_hook=None, *kwargs):
    ''' Read JSON file to Python object.
    
        Parameter(s)
        -------------
        fpath:   string or os.PathLike
        mode: 'r' to read, rb to read as bytes
        
        JSON to Python Conversion List Reminder
            JSON	PYTHON
            object*	dict    includes pandas DataFrame objects
            array	list
            string	str
            number (int)	int
            number (real)	float
            true	True
            false	False
            null	None
            
        Returns: Python object '''
        
    with open(fp, mode) as json_file:
        json_obj = json.load(json_file, *kwargs)
        json_file.close()
        return json_obj
    
def main():
    json_read(fp, mode='r', cls=dict)

if __name__ == "__main__":
    main()
