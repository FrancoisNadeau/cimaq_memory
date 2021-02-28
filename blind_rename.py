#!/usr/bin/env python3

###############################################################################
### Use to look at a set of sheets with identical values named differently. ###

import pandas as pd
import re
from pandas import DataFrame as df
from tqdm import tqdm

def lowercols(sheets):
    '''
    Converts all columns's names to lowercase
    
    Parameters
    ----------
    sheets: Sequence of dataframes
    '''
    nsheets = []
    for sheet in sheets:
        sheet = sheet.rename(columns=dict(((col.lower, col)
                                          for col in sheet.columns)))
        nsheets.append(sheet)
    return nsheets

def findblind_cols(sheets, pattern):
    ''' 
    Returns boolean dataframe mask where values match a
    pattern despite differently named columns or items
    '''
    sheets = lowercols(sheets)
    sheets2 = [df(item[1].values.tostring().decode().str.fullmatch(pattern)
                  for item in sheet.iteritems())
               for sheet in sheets]
    matched_cols = [sheet.loc[[row[0] for row
                               in sheet.iterrows()
                               if row[1].all()]].index.values.tolist()
                    for sheet in sheets2]
    return matched_cols

def check_ids(sheets, patterns):
    '''
    Inspect if a column is present sequence of DataFrames despite different names
    
    Parameters
    ----------
    sheets: Sequence of dataframes

    patterns: takes a tuple of 2 items
              tuples ('name', 'regex')
    Example: patterns = (('dccid', '(?<!\d)\d{6}(?!\d)'),
                        ('pscid', '(?<!\d)\d{7}(?!\d)'))
    Returns boolean DataFrame
    '''
    patterns = df(patterns, columns=['ids', 'patterns'])        
    return df((pd.Series((row[1]['ids'] in sheet.columns
                          for sheet in sheets), name=row[1]['ids'])
               for row in patterns.iterrows()))

def get_shortest_ind(sheets):
    ''' 
    Returns shortest index in dataframes sequence
    '''
    return next(sheet for sheet in sheets
                if sheet.shape[0] == \
                (pd.Series([sheet.shape[0]
                            for sheet in sheets]).min()))

def rename_imposter_cols(sheets, patterns): # Very cool
    ''' 
    Renames duplicated columns with a common name by matching a regex pattern.
    Useful for longitudinal studies wich could have different naming conventions        
    
    Parameters
    ----------
    sheets: Sequence of dataframes

    patterns: tuple 2 items eg.: ('name', 'regex')
    '''
    patterns = df(patterns, columns=['ids', 'patterns'])    
    patterns['imposters'] = [findblind_cols(sheets, row[1]['patterns'])
                             for row in patterns.iterrows()]
    patterns['renamers'] = [[dict(zip(row[1]['imposters'][sheet[0]],
                                  [len(row[1]['imposters'][sheet[0]])*row[1]['ids']]))
                             for sheet in enumerate(sheets)]
                            for row in patterns.iterrows()]    
    for row in patterns.iterrows():
        sheets = [sheet[1].rename(columns=row[1]['renamers'][sheet[0]])
                  for sheet in enumerate(sheets)]
    return sheets
