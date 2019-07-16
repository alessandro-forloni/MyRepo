# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 14:15:31 2019

@author: alforlon

Generic formatter for poll table

If the standard code doesn't work, this will extract the data on its own

"""

import pandas as pd
import numpy as np
from datetime import datetime
from xlpython import xlfunc, xlsub, xlarg


remove_always_cols = ['Lead', 'Sample size', 'Polling firm']

def parse_column_generic(value):
    
    try:
    
        temp = str(value)
        temp = temp.replace('?', '')
        useval = temp.split('-')[0]
        useval = useval.replace('/', '-')
        useval = useval.replace('<', '')
        return float(str(useval)[:4])
    except:
        try:
            # splecial case for who contains ('\u2013' ascii)
            return float(value[:4])
        except:
            return value
    
def parse_size_generic(x):
    
    try:
        return float(x.replace(',',''))
    except:
        return x
    
def parse_last_generic(val):
    '''
    Remove last pieces with - or / that
    are just wrong numbers
    
    '''
    
    try:
        if '\xe2\x80\x93' in val or '/' in val:
            return np.nan
        else:
            return val
    except:
        return val
    
def clean_format_generic(df):
    
    clean_df = df.copy()
    
    # clean format of data
    for col in clean_df.columns[3:]:
        
        clean_df[col].replace('[b]', np.nan, inplace=True)
        clean_df[col].replace('[a]', np.nan, inplace=True)
        clean_df[col].replace('[c]', np.nan, inplace=True)
        
        clean_df[col] = clean_df[col].apply(parse_column_generic)
        clean_df[col] = clean_df[col].apply(parse_last_generic)
        
    return clean_df
    
    
def clean_polling_firm_generic(col):
    
    '''
    Input is a Series (dataframe column)
    
    '''
    
    # just annoying
    for j in range(1,100):
        col = col.apply(lambda x: x.replace('['+str(j)+']', ''))
        
    # replace also special charachters
    col = col.apply(lambda x: x.replace('\xc3\xa9', 'e'))
    col = col.apply(lambda x: x.replace('\xc3\xb1', 'n'))
    col = col.apply(lambda x: x.replace('\xc3\xba', 'u'))
    col = col.apply(lambda x: x.replace('\xc3\xb3', 'o'))
    col = col.apply(lambda x: x.replace('\xc3\xad', 'i'))
    col = col.apply(lambda x: x.replace('\x93\xc3\x81', 'A'))
    col = col.apply(lambda x: x.replace('\xc2\xa0', ' '))
    col = col.apply(lambda x: x.replace('\xe2\x80\x93', '-'))
    
    col = col.apply(lambda x: x.replace('\xe2\x80', '-'))
    
    return col


def parse_dates_generic(date):
    
    if type(date) == float:
        
        # in such case, excel has properly read the dates        
#        try:        
        return datetime.fromordinal(datetime(1900, 1, 1).toordinal() \
                                        + int(date) - 2)
#        except:
#            return date
    try:
        cleaned_date = date.replace('\xe2\x80\x93', '-')
    except:
        cleaned_date = date
    try:
        return datetime.strptime(cleaned_date, "%d %b %Y")
    except:
        
        try:
            splitted = cleaned_date.split('-')[-1]
            return datetime.strptime(splitted, "%d %b %Y")
        except:
            return cleaned_date
        
        

def parse_table(cols, table):
    
    # get the data in input
    # excel range will be a tuple of lists
    # this needs to be converted to a dataframe
    input_list = [x for x in table]
    columns = [x for x in cols]
    df_input = pd.DataFrame(input_list, columns=columns)
    df_input.replace('',np.nan, inplace=True)
    df_input.dropna(how='all', inplace=True)
    
    return df_input


def process_generic_table(cols, table):
    
    df = parse_table(cols, table)
        
    print df
    
    # clean a bit around
    df.replace('', np.nan, inplace=True)
    df.replace('?', np.nan, inplace=True)
    df.replace('N/A', np.nan, inplace=True)
    df.replace('-', np.nan, inplace=True)
    df.replace('\xe2\x80\x93', np.nan, inplace=True)
    df.replace('Tie', np.nan, inplace=True)
    
    
#    if 'Sample size' in df.columns:
#        df['Sample size'] = df['Sample size'].apply(parse_size_generic)
    
    # clean dirty ASCII charachters    
    df = clean_format_generic(df)
    
    
    
    # Again have to replace strange dash for dates
    df['Date'] = df['Date'].apply(parse_dates_generic)
    
    # drop duplicate dates (keep-first aka the last)
    df.drop_duplicates('Date', keep='first', inplace=True)
    
    #df['Polling firm'] = clean_polling_firm_generic(df['Polling firm'])
    
    return df
    
@xlfunc
def extract_from_excel(cols, table):
    
    
    df = process_generic_table(cols, table)
    reindexed = df.set_index('Date')
    
    for x in remove_always_cols:
        if x in df.columns:    
            reindexed.drop(x, axis=1, inplace=True)
   
    df_resampled = reindexed.resample('D').last()    
    df_resampled.fillna(method='ffill', inplace=True)
    

    
    return df_resampled


@xlfunc
def get_generic_names():
    
    '''
    Columns have to be fetched separately

    '''
    
    df = resampled_italian_data()
    df_col = pd.DataFrame.from_dict({0: df.columns}, orient='Index')
    return df_col