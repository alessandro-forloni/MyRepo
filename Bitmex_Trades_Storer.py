# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 15:48:57 2018

@author: Alessandro

BITMEX TRADES EXTRACTOR

"""

import pandas as pd
import requests 
from datetime import datetime
import time
import os


file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, 'Data')

api_string = 'https://www.bitmex.com/api/v1/trade?symbol=XBTUSD&count=500&start='
bs_dict = {'Buy':1, 'Sell':-1}

#=============================================================================

#42749400
starting_point = 42749400
group_max_size = 100000


#=============================================================================



def get_data(t):
    
    req = requests.get(api_string + str(t))
    
    if req.status_code != 200:
        
        print('Error')
        return [],[],[],[]
    
    else:
        
        trades = req.json()
        
        prices = [x['price'] for x in trades]
        sides = [bs_dict[x['side']] for x in trades]
        sizes = [x['size'] for x in trades]
        
        ts = [x['timestamp'] for x in trades]
    
    return prices, sides, sizes, ts


def get_starting_point():
    
    '''
    Guarda cosa ha salvato fino ad ora e parte dal primo mancante
    
    '''
    
    files = os.listdir(data_path)
    
    if len(files) == 0:
        return starting_point
    
    
    file_names = [int(x[8:16]) for x in files]
    
    # +500 perchè vedi come è stato salvato
    return max(file_names) + 500




prices = []
sides = []
sizes = []
timestamps = []

point = get_starting_point()
counter = 0


while counter < 3:
    
    pcs,sds,szs,ts = get_data(point)
    
    
    if len(pcs) == 0:
        
        print('Some Error')
        time.sleep(10)
        continue
    
    # Stack
    prices = prices + pcs
    sides = sides  + sds 
    sizes = sizes  + szs
    timestamps = timestamps + ts
    
    print('Recorded', ts[0])
    # Salva nel dataframe e metti su csv
    # Poi resetta le variabili
    if len(prices) >= group_max_size:
        
        df = pd.DataFrame(columns = ['timestamp', 'price', 'size','side'])
        
        df['timestamp'] = timestamps
        df['price'] = prices
        df['size'] = sizes
        df['side'] = sides
        
        # Salvato con il punto da cui è stato preso l'ultimo blocco di 500
        fName = 'XBT_USD_' + str(point) + '_' + timestamps[0].replace(':','.') + '.csv'
        
        df.to_csv(os.path.join(data_path, fName))
        
        print('Saved to csv', fName)
        del df
        
        prices = []
        sides = []
        sizes = []
        timestamps = []
        
        time.sleep(5)
        
    point = point + 500
    time.sleep(3)
        
    