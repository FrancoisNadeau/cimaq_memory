#!/usr/bin/env python3

from cimaq_utils import *
from cimaq_utils import loadimages
from blind_rename import rename_imposter_cols
from inspect_misc_text import *
from zipctl import uzipfiles
from os.path import expanduser as xpu
from collections import OrderedDict

def get_infos(filepath=None, mem=False):
    ''' 
    Obtain highly detailed information about a data file
    
    Description
    -----------
    'hdr' variable:
    - Source: Source: https://stackoverflow.com/questions/15670760/built-in-function-in-python-to-check-header-in-a-text-file

    Parameters
    ----------
        filepath: string, path buffer or os-pathlike object
    
    Returns: DataFrame
    '''
    if not filepath:
        rawsheet = mem
        hdr = rawsheet[1] not in b'.-0123456789'
    else:
        rawsheet = open(filepath , "rb", buffering=0)
        hdr = rawsheet.read(1) not in b'.-0123456789'
    rawsheet.seek(0)
    test = tuple(line for line in rawsheet.readlines())
    rawsheet.seek(0)
    test2 = df((pd.Series(line.split())
                for line in rawsheet.readlines()))
    row_fields = pd.Series(int(len(row[1]))
                           for row in test2.iterrows())
    dupindex = splitrows(test2[test2.columns[0]].values.tolist())
    nlines, rowbreaks = len(test), tuple(get_doublerows(test2))
    rawsheet.seek(0)
    detector = udet()
    for line in rawsheet.readlines():
        detector.feed(line)
        if detector.done: break
    detector.close()
    encoding = detector.result['encoding']
    if encoding == None:
        encoding = 'utf8'
    rawsheet.seek(0)
    if not rowbreaks:
        rowbreaks = False
    widths = pd.Series(len(line) for line in test)
    if hdr:
        nfields = int(row_fields[1:-1].max())
        test, test2, width = test[1:], test2[1:], widths[1:].max() 
        if dupindex:
            nfields = int(row_fields[2:-1].max())
            test, test2, width = test[1:], test2[1:], widths[1:].max()
    else:
        width, nfields = widths.max(), int(row_fields[:-1].max())
    rawsheet.seek(0)
    txttest = [line.decode(encoding) for line in rawsheet.readlines()]
    dialect = csv.Sniffer().sniff(''.join(line for line in txttest))
    valuez = [splitext(bname(filepath))[0], splitext(bname(filepath))[1],
              filepath, hdr, dupindex, rowbreaks, width, nlines,
              nfields, encoding, dialect.delimiter, dialect.doublequote,
              [dialect.escapechar if dialect.escapechar != None
               else False][0], dialect.lineterminator, dialect.quotechar,
              int(dialect.quoting), dialect.skipinitialspace]
    cnames =['fname', 'ext', 'fpaths', 'has_header', 'dup_index', 'row_breaks',
             'width', 'n_lines', 'n_fields', 'encoding', 'delimiter',
             'doublequote', 'escapechar', 'lineterminator', 'quotechar', 'quoting', 'skipinitialspace']
    dialect_dict = dict(zip(cnames, valuez))
    rawsheet.close()
    return dialect_dict

def main():
    get_infos(filepath)

if __name__ == "__main__":
    main()
