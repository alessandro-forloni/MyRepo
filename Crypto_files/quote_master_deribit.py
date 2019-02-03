# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 10:42:08 2019

@author: alforlon
"""




import numpy as np
import requests 
import time
import threading
import logging
import os
from collections import defaultdict


file_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(file_path, 'log')


class QuoteManager(threading.Thread):
    
    def __init__(self, N, pair, timeout = 2, round_lev = 1):
        
        '''
        
        N indica dimensione del vettore
        pair e' exchange name della coppia
        
        '''
        self.N = N
        self.ROUND_LEV = round_lev
        
        self.price_vector = []  #conterra' i prezzi da mostrare nel book
        self.bid_vector = []
        self.ask_vector = []
        self.bid_qty_vector = []
        self.ask_qty_vector = []
        
        # per costruire order book
        self.price_grid = []
        self.ref_point = np.nan
        self.mid_point = np.nan
        self.ix_ref = np.nan
        
        #self.tstamp = np.nan*np.zeros(N)
        
        self.timeout = timeout
        self.last_call = 0 # tiene traccia di quando l'ultima chiamata e' stata fatta
        self.api_string = self.generate_api(pair, self.N)
        
        # Attiva o disattiva il modulo (di base e' sempre attivo)
        self.active = True
        
        # Thread Initialization
        threading.Thread.__init__(self)
        
        
        
        # Inizializza il logger (riscrivendo il log file)
#        fh=logging.FileHandler(os.path.join(log_path, pair+'.log'))
#        
#        # Setta il formato
#        formatter = logging.Formatter('%(asctime)s;%(message)s')
#        fh.setLevel(logging.INFO)
#        fh.setFormatter(formatter)
        
        # definisci il logger specifico
#        self.logger = logging.getLogger(pair)#os.path.join(log_path, pair)+'.log')
#        self.logger.setLevel(logging.INFO)
#        self.logger.addHandler(fh)
        
        self.temp = None
        
    @staticmethod
    def generate_api(pair, N):
        
        '''
        genera api string data una coppia
        e ritorna anche string per prendere dati da API
        
        '''
        #https://www.deribit.com/api/v1/public/getorderbook?instrument=BTC-PERPETUAL&depth=2
        api_root = 'https://www.deribit.com/api/v1/public/getorderbook?instrument=BTC-PERPETUAL'
        api_string = api_root + '&depth=' + str(N)
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
                ob = req.json()
               
                self.temp = ob
                
                bid_prices = [x['price'] for x in ob['result']['bids']]
                ask_prices = [x['price'] for x in ob['result']['asks']]
   
                bid_qtys = [x['quantity'] for x in ob['result']['bids']]
                ask_qtys = [x['quantity'] for x in ob['result']['asks']]      

                
            except:
                print('\nError with JSON for '+self.pair)
                #self.logger.info(self.get_log_msg(np.nan, np.nan, np.nan, np.nan))  
                return None, None, None, None
                
        #self.logger.info(self.get_log_msg(bid_price, ask_price, bid_qty, ask_qty))  
        
        return bid_prices, ask_prices, bid_qtys, ask_qtys
    
    
    def update_vectors(self):
        
        # get data
        bid_price, ask_price, bid_qty, ask_qty = self.request_prices()
        
        
        if bid_price is not None and bid_qty is not None:
            
            # Aggiorna vettori
            self.bid_vector = bid_price
            self.ask_vector = ask_price
            self.bid_qty_vector = bid_qty
            self.ask_qty_vector = ask_qty
            
            self.price_vector = self.bid_vector[::-1] + self.ask_vector
        
            return 1
        
        else:
            
            print 'Error parsing book...'
            return 0
        
        

        
        
    @staticmethod
    def shift_vector(vec, newval):
        
        '''
        attacca prezzo alla fine
        e shifta il resto di uno
        
        '''
        
        vec[:-1] = vec[1:]
        vec[-1] = newval
        
        return vec
    
    
    def stop(self):
        
        self.active = False
        
        
    def restart(self):
        
        self.price_vector = []  #conterra' i prezzi da mostrare nel book
        self.bid_vector = []
        self.ask_vector = []
        self.bid_qty_vector = []
        self.ask_qty_vector = []
        
#        self.price_vector = np.nan*np.zeros(self.N)  #conterra' i mid prices
#        self.bid_vector = np.nan*np.zeros(self.N) 
#        self.ask_vector = np.nan*np.zeros(self.N) 
#        self.bid_qty_vector = np.nan*np.zeros(self.N) 
#        self.ask_qty_vector = np.nan*np.zeros(self.N)
        
        self.active = True
        
        
    def work(self):
        
        ''' 
        
        fa andare il quote manager
        tiene il tempo in modo da fare una richiesta ogni timeout
        
        '''
        
        
        while self.active == True:
                        
            self.update_vectors()
            

    def get_price(self):
        
        '''
        Getter per il mid price.
        Principalmente usato dal calculator
        
        QUI LOGGO TUTTO
        
        '''
#        self.logger.info(self.get_log_msg(self.bid_vector[-1], self.ask_vector[-1], \
#                                          self.bid_qty_vector[-1], self.ask_qty_vector[-1]))  
        
        return 0#self.price_vector[-1]
    
    
    def get_bid(self):
        
        '''
        Getter per il bid price.
        Principalmente usato dal PosMgr
        
        '''
        
        return self.bid_vector[0]
    
    def get_ask(self):
        
        '''
        Getter per l'ask.
        Principalmente usato dal PosMgr
        
        '''
        
        return self.ask_vector[0]
            
            
    def get_price_table(self, book_size, ROUND_LEV=2):
        
        '''
        prende il book e vede quanto puo' far stare nel book
        e come allineare
        
        '''
        
        if self.price_vector == []:
            return None, None, None
        
        incr = 0.25#1/10**ROUND_LEV
        
        # calcola tutti i prezzi presenti
        price_grid = np.round(np.arange(self.price_vector[0], self.price_vector[-1], incr),ROUND_LEV)
        qty_vector =  self.bid_qty_vector[::-1] + self.ask_qty_vector 
        
        book_dict = dict(zip(np.round(self.price_vector,ROUND_LEV), qty_vector))
        book_default_dict = defaultdict(lambda:'', book_dict)
        
        # prendi il mid arrotondato in modo che combaci con un punto della griglia
        #mid = round((self.bid_vector[0] + self.ask_vector[0])/2, 0)
        
        # trova l'indice del primo ask sulla griglia
        ix = np.where(np.round(price_grid,ROUND_LEV) == np.round(self.ask_vector[0],ROUND_LEV))[0][0]
        
        # vedi che livelli mettere nel book
        bid_levels = list(price_grid[ix-int(book_size/2):ix])
        ask_levels = list(price_grid[ix:ix+int(book_size/2)])
        
        
        bid_qtys = [book_default_dict[round(x,ROUND_LEV)] for x in bid_levels] + ['']*int(book_size/2)
        ask_qtys = ['']*int(book_size/2) + [book_default_dict[round(x,ROUND_LEV)] for x in ask_levels] 
        
        return bid_levels+ask_levels, bid_qtys, ask_qtys
    


    def get_moving_price_table(self, book_size, ROUND_LEV=2):
        
        '''
        prende il book e vede quanto puo' far stare nel book
        tenendo una finestra fissa di prezzi se possibile
        
        '''
        
        if self.price_vector == []:
            return None, None, None
        
        incr = 0.25
        
        # se la griglia e' troppo spostata, aggiornala
        if np.abs(self.ref_point - self.mid_point) > book_size*incr/4 or self.price_grid == []: 
            
            self.price_grid = np.round(np.arange(self.price_vector[0], self.price_vector[-1], incr),ROUND_LEV)
            print('Refreshed the grid...')
            # trova l'indice del primo ask sulla griglia, solo al momemnto 
            # in cui si entra in questo ciclo
            self.ref_point = np.round(self.ask_vector[0],ROUND_LEV)
            ix_ref = np.where(np.round(self.price_grid,ROUND_LEV) == self.ref_point)[0][0]
            self.ix_ref_down = ix_ref-int(book_size/2)
            self.ix_ref_up = ix_ref+int(book_size/2)


        # come prima trova il mid
        self.mid_point = np.round(self.ask_vector[0],ROUND_LEV)   
        ix = np.where(np.round(self.price_grid,ROUND_LEV) == self.mid_point)[0][0]
        
        # vedi che livelli mettere nel book
        bid_levels = list(self.price_grid[self.ix_ref_down:ix])
        ask_levels = list(self.price_grid[ix:self.ix_ref_up])
        
        
        # il resto come prima
        qty_vector =  self.bid_qty_vector[::-1] + self.ask_qty_vector 
        
        book_dict = dict(zip(np.round(self.price_vector,ROUND_LEV), qty_vector))
        book_default_dict = defaultdict(lambda:'', book_dict)
        
        
        bid_qtys = [book_default_dict[round(x,ROUND_LEV)] for x in bid_levels] + ['']*(self.ix_ref_up-ix)
        ask_qtys = ['']*(ix-self.ix_ref_down) + [book_default_dict[round(x,ROUND_LEV)] for x in ask_levels] 
        
        return bid_levels+ask_levels, bid_qtys, ask_qtys 
    
    
#%%
#book_size = 50
#ROUND_LEV = 2
#    
#       
#incr = 0.25#1/10**ROUND_LEV
#
## vedi dove e' messa la griglia
#grid_mid = (qm.price_vector[0] + qm.price_vector[-1])/2
#
## se la griglia e' troppo spostata, aggiornala
#if np.abs(qm.ref_point - grid_mid) > book_size*incr/2 or qm.price_grid == []: 
#    qm.price_grid = np.round(np.arange(qm.price_vector[0], qm.price_vector[-1], incr),ROUND_LEV)
#    print('Refreshed the grid...')
#    
## il resto come prima
#qty_vector =  qm.bid_qty_vector[::-1] + qm.ask_qty_vector 
#
#book_dict = dict(zip(np.round(qm.price_vector,ROUND_LEV), qty_vector))
#book_default_dict = defaultdict(lambda:'', book_dict)
#
## prendi il mid arrotondato in modo che combaci con un punto della griglia
##mid = round((self.bid_vector[0] + self.ask_vector[0])/2, 0)
#
## trova l'indice del primo ask sulla griglia
#qm.ref_point = np.round(qm.ask_vector[0],ROUND_LEV)
#ix = np.where(np.round(qm.price_grid,ROUND_LEV) == qm.ref_point)[0][0]
#
## vedi che livelli mettere nel book
#bid_levels = list(qm.price_grid[ix-int(book_size/2):ix])
#ask_levels = list(qm.price_grid[ix:ix+int(book_size/2)])
#
#
#bid_qtys = [book_default_dict[round(x,ROUND_LEV)] for x in bid_levels] + ['']*int(book_size/2)
#ask_qtys = ['']*int(book_size/2) + [book_default_dict[round(x,ROUND_LEV)] for x in ask_levels] 
