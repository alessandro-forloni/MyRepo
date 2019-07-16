# -*- coding: utf-8 -*-
"""
Created on Fri May 31 10:03:33 2019

@author: alforlon

Fetching data on Italian Election Polls

"""
import requests as requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
from xlpython import xlfunc, xlsub, xlarg

data_link = 'https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_Italian_general_election'

def parse_column_it(value):
    
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
    
def parse_size_it(x):
    
    try:
        return float(x.replace(',',''))
    except:
        return x
    
def parse_last_it(val):
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
    
def clean_format_it(df):
    
    clean_df = df.copy()
    
    # clean format of data
    for col in clean_df.columns[3:]:
        
        clean_df[col].replace('[b]', np.nan, inplace=True)
        clean_df[col].replace('[a]', np.nan, inplace=True)
        clean_df[col].replace('[c]', np.nan, inplace=True)
        
        clean_df[col] = clean_df[col].apply(parse_column_it)
        clean_df[col] = clean_df[col].apply(parse_last_it)
        
    return clean_df
    
    
def clean_polling_firm_it(col):
    
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


def parse_dates_it(date):
    
    try:
        return datetime.strptime(date+' 2019', "%d %b %Y")
    except:
        
        try:
            splitted = date.split('-')[-1]
            return datetime.strptime(splitted+' 2019', "%d %b %Y")
        except:
            return date
        
        

def parse_table():
    
    # get the data
    req = requests.get(data_link).text
    soup = BeautifulSoup(req,'html.parser')
    
    # get the tbody
    table = soup.find('table', {'class':'wikitable'}).find('tbody')
    table_structure = table.findAll('tr')
    
    table_dict = {}
    collect = []
    # now we have to dig row by row excluding the first three
    for i in range(3, len(table_structure)):
        
        row = table_structure[i].findAll('td')
        row_text = [x.text.replace('\n','').replace('?','').encode('utf8') for x in row]
        
        if len(row_text) < 15:
            collect.append(row)
            continue
        
        table_dict[i] = row_text # create it and clean it for export
        
    
    df = pd.DataFrame.from_dict(table_dict, orient='index')
    
    return df


def process_italian_table():
    
    df = parse_table()
        
     # clean data
    df.columns = ['Date', 'Polling firm', 'Sample size', 'M5S',
                  'PD', 'Lega', 'FI', 'FdI', 'Sin','+Eu', 'EV', 'Other',
                  'Lead', 'Govt Parties', 'Other_2'
                  ]
    
    
    # clean a bit around
    df.replace('', np.nan, inplace=True)
    df.replace('?', np.nan, inplace=True)
    df.replace('N/A', np.nan, inplace=True)
    df.replace('-', np.nan, inplace=True)
    df.replace('\xe2\x80\x93', np.nan, inplace=True)
    df.replace('Tie', np.nan, inplace=True)
    
    #special for Nuovo centro Italiano
#    df['NcI'].replace('w. FI', 0.0, inplace=True)
    
    df['Sample size'] = df['Sample size'].apply(parse_size_it)
    df = clean_format_it(df)
    
    
    
    # Again have to replace strange dash for dates
    df['Date'] = df['Date'].apply(lambda x: x.replace('\xe2\x80\x93', '-'))
    df['Date'] = df['Date'].apply(parse_dates_it)
    
    # drop duplicate dates (keep-first aka the last)
    df.drop_duplicates('Date', keep='first', inplace=True)
    
    df['Polling firm'] = clean_polling_firm_it(df['Polling firm'])
    
    return df
    
@xlfunc
def resampled_italian_data():
    
    
    df = process_italian_table()
    reindexed = df.set_index('Date')
    reindexed.drop('Polling firm', axis=1, inplace=True)
    reindexed.drop('Sample size', axis=1, inplace=True)
    reindexed.drop('Lead', axis=1, inplace=True)
    reindexed.drop('Govt Parties', axis=1, inplace=True)
    reindexed.drop('Other_2', axis=1, inplace=True)
   
    df_resampled = reindexed.resample('D').last()
    
    df_resampled.fillna(method='ffill', inplace=True)
    
    # add columns to coerce with past data
    df_resampled.insert(5, 'NcI', '')
    df_resampled.insert(7, 'Leu', '')
    df_resampled.insert(9, 'PaP', '')
    
    return df_resampled


@xlfunc
def get_italian_names():
    
    '''
    Columns have to be fetched separately

    '''
    
    df = resampled_italian_data()
    df_col = pd.DataFrame.from_dict({0: df.columns}, orient='Index')
    return df_col
    


#if __name__ == '__main__':
#
#    df = resampled_italian_data()