# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 09:04:42 2018

@author: Alessandro

UCG-ISP Intraday spread

"""

from xlwings import Book, Range
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os

#===========================================================

bid_1_n = 'A1'
bid_1   = 'B1'
ask_1   = 'C1'
ask_1_n = 'D1'

ref_1 = 17.234
ref_2 = 3.083

#Roughly 15 mins
N = 360

#=============================================================================

def stack(v, elem):
    
    #v must be numpy!!

    v_new = np.roll(v,-1)
    v_new[-1] = elem
    
    return v_new

def init_book():
    
    Range('A1').value = "Bid_Qty"
    Range('B1').value = "Bid_Price"
    Range('C1').value = "Ask_Price"
    Range('D1').value = "Ask_Qty"
    Range('E1').value = "Last"
    Range('F1').value = "Volume"
    Range('G1').value = "Ref_Close"
    
def set_book(ticker, line):
    
    Range('A' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";bid_num_1\'"
    Range('B' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";bid\'"
    Range('C' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";ask\'"
    Range('D' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";ask_num_1\'"
    Range('E' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";last\'"
    Range('F' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";volume\'"
    #Add ref close for simplicity
    Range('G' + str(line + 1)).value = "=FDF|Q!\'"+ ticker + ";close\'"

    return 0

def get_quotes():
    
    print(Range('E1').value, ' || ' , Range('E2').value)
    
def attach_quotes():
    
    return (Range('B2').value, Range('B3').value, \
            Range('C2').value, Range('C3').value)

def get_volume_data():
    
    return (Range('E2').value, Range('E3').value, \
            Range('F2').value, Range('F3').value)
    
def get_ref_closes():
    
    return (Range('G2').value, Range('G3').value)
    
#=============================================================================
    

savePath = os.path.dirname(os.path.abspath(__file__))

wb = Book()
time.sleep(5)

init_book()

set_book('UCG.MI', 1)

set_book('ISP.MI', 2)
time.sleep(5)


bid_1 = np.zeros(N)
bid_2 = np.zeros(N)

ask_1 = np.zeros(N)
ask_2 = np.zeros(N)

last_1 = np.zeros(N)
last_2 = np.zeros(N)

vol_1 = np.zeros(N)
vol_2 = np.zeros(N)

time_list = ['']*N


counter = 0

print '\nStart Recording...\n'

c1, c2 = get_ref_closes()

#Set reference prices
ref_1 = c1
ref_2 = c2

print 'Reference closes:', c1, c2

while True:
    
    try:
        
        b1,b2,a1,a2 = attach_quotes()
        l1,l2,v1,v2 = get_volume_data()
        
        adesso = datetime.datetime.strftime(datetime.datetime.now(), \
                '%d-%m-%Y %H:%M:%S')
         
    except:
        
        adesso = datetime.datetime.strftime(datetime.datetime.now(), \
                '%d-%m-%Y %H:%M:%S')
        
        print 'Error reading data', adesso
        continue

    
    
#    print b1, b2, a1, a2, l1, l2, v1, v2
    
    bid_1 = stack(bid_1, b1/ref_1)
    bid_2 = stack(bid_2, b2/ref_2)
    ask_1 = stack(ask_1, a1/ref_1)
    ask_2 = stack(ask_2, a2/ref_2)
    
    last_1 = stack(last_1, l1/ref_1)
    last_2 = stack(last_2, l2/ref_2)
    vol_1 = stack(vol_1, v1/ref_1)
    vol_2 = stack(vol_2, v2/ref_2)
    
    time_list[counter] = adesso
 

    if counter == N-1:
        
        #SAVE DATA
        df = pd.DataFrame(bid_1, columns = ['Bid_1'])
        df['Ask_1'] = ask_1
        df['Bid_2'] = bid_2
        df['Ask_2'] = ask_2
        df['Last_1'] = last_1
        df['Last_2'] = last_2
        df['Volume_1'] = vol_1
        df['Volume_1'] = vol_2
        df['Timestamp'] = time_list
        
        adesso = datetime.datetime.strftime(datetime.datetime.now(), \
                '%d-%m-%Y-%H.%M.%S')
        
        #Put before, just to check
        print 'Saved', adesso
         
         
        df.to_csv(savePath + '\\' + adesso + '.csv')
        
       
        counter = 0
        
    else:
        
        counter = counter + 1
        time.sleep(2.5)
    
    
    
    