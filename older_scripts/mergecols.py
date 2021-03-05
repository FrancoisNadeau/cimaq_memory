#!/usr/bin/env python

import pandas as pd

'''
Source: https://towardsdatascience.com/how-to-clean-and-combine-dataframe-columns-of-lists-ebd3542559b6
'''

def create_df_from_listentry(df, col_name):
    '''
    Takes a column of lists (col_name) from a dataframe (df)
    
    Returns a dataframe with number of columns equal to max list size 
    and each element of the row list in its own column  
    '''
    new_df = df[col_name].apply(pd.Series)
    new_df = new_df.rename(columns = lambda x : col_name + '_' + str(x))
    return new_df
    
def create_dummy_from_listentries(df, col_name):
    '''
    Takes a column of lists (col_name) from a dataframe (df)
    
    Returns a dataframe with dummy variables representing
    each unique element of the lists in aggregate
    '''
    list_df = create_df_from_listentry(df, col_name)
    df_cols = list_df.columns.tolist()
    df_dummy = pd.DataFrame()
    for col in df_cols:
        if df_dummy.empty:
            df_dummy = pd.get_dummies(list_df[col])
        else:
            df_dummy.add(pd.get_dummies(list_df[col])) 
    return df_dummy

def strip_strlist(list_to_strip):
    return [item for item in list_to_strip if type(item) == str]

def merge_cols(df, col_names):
    '''
    Assuming col_names in df that contain lists of strings, 
    merge the lists by row and return the combined col as a list
    
    If single [col_name], returns a list that replaces 
    NaN entries with [] 
    '''
    joined_df = pd.DataFrame()
    for col in col_names:
        if joined_df.empty:
            joined_df = create_df_from_listentry(df, col)
        else:
            tojoin_df = create_df_from_listentry(df, col)
            joined_df = joined_df.join(tojoin_df)
    
    joined_list = joined_df.values.tolist()
    joined_list_dropna = [strip_strlist(list_entry) for list_entry in joined_list]
    merged_set = list(map(set, joined_list_dropna))
    merged_list = list(map(list, merged_set))

    return merged_list
    
def list_to_df_col(source_list, source_df, col_name):
    '''
    Returns a DataFrame with a single col_name, 
    data from source_list and index based on source_df
    '''
    df = pd.DataFrame(index=source_df.index)
    df[col_name] = source_list

    return df
    