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
    
    def __init__(self, N, pair, timeout = 2):
        
        '''
        
        N indica dimensione del vettore
        pair e' exchange name della coppia
        
        '''
        self.N = N
        
        self.price_vector = []  #conterra' i prezzi da mostrare nel book
        self.bid_vector = []
        self.ask_vector = []
        self.bid_qty_vector = []
        self.ask_qty_vector = []
        #self.tstamp = np.nan*np.zeros(N)
        
        self.timeout = timeout
        self.last_call = 0 # tiene traccia di quando l'ultima chiamata e' stata fatta
        self.api_string, self.api_getter = self.generate_api(pair, self.N)
        
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
        
        api_root = 'https://api.kraken.com/0/public/Depth?count=&' + str(N) + '&pair='
        
        getter_string = 'X' + pair[:3] + 'Z' + pair[3:]
        
        return api_root + pair, getter_string
        

    @staticmethod
    def get_log_msg(bid_price, ask_price, bid_qty, ask_qty):
        
        '''
        Uso per creare il messaggio del log in formato decente
        '''
        msg = str(bid_price)+';'+str(ask_price)+';'+str(bid_qty)+';'+str(ask_qty)
        #print msg
        return msg
        
    
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
                level_2 = req.json()
               
                self.temp = level_2
                
                bid_levels = map(list, zip(*level_2['result'][self.api_getter]['bids']))[0]
                ask_levels = map(list, zip(*level_2['result'][self.api_getter]['asks']))[0]
   
                bid_quants = map(list, zip(*level_2['result'][self.api_getter]['bids']))[1]
                ask_quants = map(list, zip(*level_2['result'][self.api_getter]['asks']))[1]             
                
                bid_prices = [round(float(x),1) for x in bid_levels[:self.N*2]]
                bid_qtys = [float(x) for x in bid_quants[:self.N*2]]
                
                ask_prices = [round(float(x),1) for x in ask_levels[:self.N*2]]
                ask_qtys = [float(x) for x in ask_quants[:self.N*2]]
            
                
                
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
            
            
    def get_price_table(self, book_size):
        
        '''
        prende il book e vede quanto puo' far stare nel book
        e come allineare
        
        '''
        
        if self.price_vector == []:
            return None, None, None
        
        # calcola tutti i prezzi presenti
        price_grid = np.round(np.arange(self.price_vector[0], self.price_vector[-1], 0.1),1)
        qty_vector =  self.bid_qty_vector[::-1] + self.ask_qty_vector 
        
        book_dict = dict(zip(np.round(self.price_vector,1), qty_vector))
        book_default_dict = defaultdict(lambda:'', book_dict)
        
        # prendi il mid arrotondato in modo che combaci con un punto della griglia
        mid = round((self.bid_vector[0] + self.ask_vector[0])/2, 1)
        
        # trova l'indice sulla griglia
        ix = np.where(np.round(price_grid,1) == mid)[0][0]
        
        # vedi che livelli mettere nel book
        bid_levels = list(price_grid[ix-int(book_size/2):ix])
        ask_levels = list(price_grid[ix:ix+int(book_size/2)])
        
        
        bid_qtys = [book_default_dict[round(x,1)] for x in bid_levels] + ['']*int(book_size/2)
        ask_qtys = ['']*int(book_size/2) + [book_default_dict[round(x,1)] for x in ask_levels] 
        
        return bid_levels+ask_levels, bid_qtys, ask_qtys
            
            