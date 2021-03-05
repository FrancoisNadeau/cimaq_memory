#!/usr/bin/env python3

import json
import os
from typing import Union

def json_write(fp: Union[str, os.PathLike], obj, skipkeys=False, ensure_ascii=True,
              check_circular=True, allow_nan=True, cls=None, indent=None, separators=None,
              default=None, sort_keys=False, **kwargs):
    ''' Read JSON file to Python object using a safe context-manager or 'buffer'
    
        Parameter(s)
        -------------
        fpath:   string or os.PathLike
        
        JSON to Python Conversion List Reminder
            JSON	PYTHON
            object*	dict    *includes pandas DataFrame objects
            array	list
            string	str
            number (int)	int
            number (real)	float
            true	True
            false	False
            null	None
            
        Returns: Python object '''
        
    with open(fp, 'w') as json_file:
        json.dump(obj, json_file, **kwargs)        
        json_file.close()
    
def main():
    json_write(fp, obj=None, skipkeys=False, ensure_ascii=True, check_circular=True,
               allow_nan=True, cls=None, indent=None, separators=None,
               default=None, sort_keys=False)

if __name__ == "__main__":
    main()
