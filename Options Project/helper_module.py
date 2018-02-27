# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 17:40:31 2018

@author: Alessandro

HELPER MODULE

GIVEN ONE SET OF PUTS OR VIX CALLS
COMPUTES DAILY PNL ALONG THEIR LIFE

PLUS FUNCTIONS TO GET TRADING DATE


"""
import numpy as np
import datetime
import time
import pandas as pd


def daily_pnl_calc(data, file_list, start, stop, expiry, strike_1, strike_2, premium, q, underlying):
    
    """
    Parameters:
    
        - dictionary of dataframes
        - list of file names to call
        - start index
        - end index
        - Expiry date as a string
        - strike put 1 (or VIX)
        - strike put 2 (zero)
        - premium that is the amount paid on position (positive for S&P option put spread)
        - Number of VIX options purchased
        - underlying: VIX/S&P as in Excel file
        
    """ 
    pnl = np.zeros(len(file_list))
    
    #Pnls are set at zero to start
    #In the other days is price of positon -initial value

    #Consider also IB commissions  
    if underlying == '^VIX':    
        
        vix_size = 0.7*(premium >= 0.1)  \
                   +  0.25*(premium < 0.05)   \
                   +  0.5*(premium >= 0.05 and premium < 0.1)
                   
        vix_comm = max(1, q*vix_size)           
    
    
    for i in range(start+1,stop+1):
        
        #Open data
        dff = data[file_list[i]]
        
        #Filter
        dff = dff[dff['expiration'] == expiry]
        dff = dff[dff['underlying_symbol'] == underlying]
        
        if underlying == '^SPX':
            
            dff = dff[dff['option_type'] == 'P']
            
            try:
                
                #Locate strikes
                ix_1 = dff['strike'][dff['strike'] == strike_1].index[0]
                ix_2 = dff['strike'][dff['strike'] == strike_2].index[0]
                               
                                        
                #At maturity assume liquidating at mid price
                pnl[i] =  premium - \
                          (dff['bid_1545'][ix_1] + dff['ask_1545'][ix_1])/2 \
                          + (dff['bid_1545'][ix_2] + dff['ask_1545'][ix_2])/2
                    
                    
            except(IndexError):
            
                #print 'Issue on', file_list[i]
                pnl[i] = pnl[i-1]
                
                continue
        
                 
            
        elif underlying == '^VIX':
            
            dff = dff[dff['option_type'] == 'C']
            
            
            #ALTERNATIVE WITH IF AND SEE SPEED
            try:
                
                #Locate option
                ix_1 = dff['strike'][dff['strike'] == strike_1].index[0]
                               
                #Assuming liquidating at mid price
                pnl[i] =  q*((dff['bid_1545'][ix_1] + dff['ask_1545'][ix_1])/2 \
                          + premium) - vix_comm

                          
            except(IndexError):
            
                #print 'Issue on', file_list[i]
                
                pnl[i] = pnl[i-1]
                
                continue            
            

    pnl[i+1:] = pnl[i]
    
           
           
    return pnl





#Finds nearest element to pivot
def nearest(items, pivot):
        return min(items, key = lambda x: abs(x - pivot))





#Finds the previous nearest to pivot
def nearest_prev(items, pivot):
        return min(items, key = lambda x: abs(x - pivot) if x <= pivot \
                   else abs(x - pivot) + datetime.timedelta(1000))


                   
#Finds the previous nearest to pivot (strictly previous)
def nearest_prev_strictly(items, pivot):
        return min(items, key = lambda x: abs(x - pivot) if x < pivot \
                   else abs(x - pivot) + datetime.timedelta(1000))
                   

              

def nearest_next(items, pivot):
    
        right_dates = [x for x in items if x >= pivot]
        
        
        if (len(right_dates) == 0):
            #Returndummy date that will not be accepted
            return datetime.datetime(1970, 1, 1, 0, 0)
            
        return min(right_dates, key = lambda x: abs(x - pivot))   
        
  

      
def locate_maturity(data, maturity):
    
    #dates is a list of datetimes
    
    #Convert maturity to string
    mat_string = datetime.datetime.strftime(maturity, "%Y-%m-%d") 
    counter_back = 0
    
    
    while True:
        
        #Try opening file backwards
        date_try_string = datetime.datetime.strftime(maturity - \
                          datetime.timedelta(counter_back), "%Y-%m-%d") 

        try:

            df = data['UnderlyingOptionsEODCalcs_' + date_try_string + '.csv']
            df = df[df['expiration'] == mat_string]
        
            
            if df['trade_volume'].sum() != 0:
                
               return date_try_string
                
                
        except:
            
            pass
                
    
        counter_back = counter_back + 1 
    
    
    
    
def nearest_couple(dates_1, dates_2, today, min_dist, max_dist):
    
    #dates_1 are S&P, dates_2 are VIX
    #max_dist and min_dist sets the range of admissible maturities
    
    N = len(dates_1)
    M = len(dates_2)
    

    date_dist = np.zeros([N,M])
    
    
    for i in range(0,N):
        
        #Distance from today to selected date
        dist_today = (dates_1[i] - today).days 
           
        
        for j in range(0,M):
            
            #Remember compute distances as VIX - S&P (must be positive)
            dist = dates_2[j] - dates_1[i]
            
                       
            
            in_range = 1*(dist_today <= max_dist and dist_today >= min_dist)
            
            
            if dist.days >= 0 and in_range == 1:
                
                date_dist[i,j] = dist.days
                
            else:
                
                #Set high random number
                date_dist[i,j] = 1000
       
    #Handle the case when there is no feasible couple            
    if np.sum(date_dist) == N*M*1000:
        
        #return combination that will surely not be traded 
        # because of eccesive date dist in the calling code
        return (0, M-1)
        
        
    #Terrible way to return list of indices of dates    
    return np.unravel_index(np.argmin(date_dist, axis=None), date_dist.shape)
    


    
def underwater_curve(PnL):
    
    #Computes underwater curve from PnL
    
    curr_max = PnL[0]
    underwater = np.zeros(len(PnL))
    
    
    for i in range(1,len(PnL)):
        
        if(PnL[i] > curr_max):
            
            curr_max = PnL[i]
            underwater[i] = 0
            
            pass
        
        else:
            
            underwater[i] = PnL[i]/curr_max - 1
            
            
    return underwater*(underwater<0)*100
            
            
            
