#!/usr/bin/env python3

import csv
import os

from typing import Union

def dict2csv(
    dict_data: dict,
    csv_file: Union[str, os.PathLike],
    csv_columns: Union[list, tuple] = None
) -> None:
    """ https://www.tutorialspoint.com/How-to-save-a-Python-Dictionary-to-CSV-file """
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")
    
def main():
    dict2csv(dict_data, csv_file, csv_columns = None)

if __name__ == "__main__":
    main()
