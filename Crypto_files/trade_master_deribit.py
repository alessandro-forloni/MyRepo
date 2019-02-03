# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 19:18:07 2019

@author: alforlon

PRENDE E PLOTTA I TRADES DI DERIBIT

"""



import numpy as np
import requests 
import time
import threading
import os
from collections import defaultdict


file_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(file_path, 'log')


class TradeManager(threading.Thread):
    
    def __init__(self, N, window = 1000, timeout = 2):
        
        '''
        
        N indica dimensione del vettore
        pair e' exchange name della coppia
        
        '''
        self.N = N
        self.WINDOW = window
        
        self.qty_vector = np.zeros(window)  #conterra' i prezzi da mostrare nel book
        self.price_vector = np.zeros(window)
        self.side_vector = np.zeros(window)
        self.time_vector = np.zeros(window)

        
        self.last_timestamp = 0
        
        #serve per recuperare tutti I trades al primo colpo
        self.first_call = True
        
        self.timeout = timeout
        self.last_call = 0 # tiene traccia di quando l'ultima chiamata e' stata fatta
        self.api_string = self.generate_api(self, self.N)
        
        # Attiva o disattiva il modulo (di base e' sempre attivo)
        self.active = True
        
        # Thread Initialization
        threading.Thread.__init__(self)
        

        self.temp = None
        
    @staticmethod
    def generate_api(self, N, first_call=False):
        
        '''
        genera api string data una coppia
        e ritorna anche string per prendere dati da API
        
        '''
        #https://www.deribit.com/api/v1/public/getorderbook?instrument=BTC-PERPETUAL&depth=2
        api_root = 'https://www.deribit.com/api/v1/public/getlasttrades?instrument=BTC-PERPETUAL'
        
        if self.first_call == True:
            # prenditi tutti i trades al primo colpo
            api_string = api_root + '&count=' + str(self.WINDOW)
            self.first_call = False
        else:
            api_string = api_root + '&count=' + str(N)
            
        return api_string
                
    
    def request_prices(self):
        
        '''
        prende una nuova riga
        
        '''

        now = time.clock()
        delta = now - self.last_call
        time.sleep(max(0,self.timeout-delta))
        
        try:
            req = requests.get(self.api_string)
            self.last_call = time.clock()
            
        except:
            
            time.sleep(0.3)
            
            try:
                
                if self.first_call:
                    req = requests.get(self.api_string, first_call = True)
                else:
                    req = requests.get(self.api_string)
                
                self.last_call = time.clock()
                
            except:
                
                print('\nError requesting data...')
                #self.logger.info(self.get_log_msg(np.nan, np.nan, np.nan, np.nan))
                return np.nan, np.nan, np.nan, np.nan
        
        if req.status_code != 200:
            
            print('\nError...')
            #self.logger.info(self.get_log_msg(np.nan, np.nan, np.nan, np.nan))
            return np.nan, np.nan, np.nan, np.nan
        
        else:
            
            try:
                trades = req.json()
               
                self.temp = trades
                
                qtys = [x['quantity'] for x in trades['result']]
                levels = [x['price'] for x in trades['result']]
                sides = [x['direction'] for x in trades['result']]
                timestamps = [x['timeStamp'] for x in trades['result']]
                
            except:
                print('\nError with JSON for '+self.pair)
                #self.logger.info(self.get_log_msg(np.nan, np.nan, np.nan, np.nan))  
                return None, None, None, None
                
        #self.logger.info(self.get_log_msg(bid_price, ask_price, bid_qty, ask_qty))  
        
        return qtys, levels, sides, timestamps
    
    
    def update_vectors(self):
        
        # get data
        qtys, levels, sides, timestamps = self.request_prices()
        
        if qtys is not None and levels is not None:    
            new_stamps = np.where(np.array(timestamps) > self.last_timestamp)[0]    
 
            if len(new_stamps) > 0:
                
                self.last_timestamp = timestamps[0]
                        
                # Aggiorna vettori
                self.qty_vector = self.shift_vector(self, self.qty_vector, qtys[new_stamps[0]:])
                self.price_vector = self.shift_vector(self, self.price_vector, levels[new_stamps[0]:])
                self.side_vector = self.shift_vector(self, self.side_vector, sides[new_stamps[0]:])
                self.time_vector = self.shift_vector(self, self.time_vector, timestamps[new_stamps[0]:])
                
        
            return 1
        
        else:
            
            print 'Error parsing book...'
            return 0
        
        

        
        
    @staticmethod
    def shift_vector(self, vec, newvals):
        
        '''
        attacca prezzo alla fine
        e shifta il resto di uno
        
        '''
        
        l = len(newvals)
        
        if l == self.WINDOW:
            vec = np.array(newvals)
            return vec
        
        vec[:-l] = vec[-l:]
        vec[-l:] = newvals
        
        return vec
    
    
    def stop(self):
        
        self.active = False
        
        
    def restart(self):
        
        self.qty_vector = []  #conterra' i prezzi da mostrare nel book
        self.price_vector = []
        self.side_vector = []
        self.time_vector = []
        
        self.active = True
        
        
    def work(self):
        
        ''' 
        
        fa andare il quote manager
        tiene il tempo in modo da fare una richiesta ogni timeout
        
        '''
        
        
        while self.active == True:
                        
            self.update_vectors()
            


            
            
    def get_trades(self):

        return self.price_vector, self.qty_vector, self.side_vector, self.time_vector     

        
    
    

    
