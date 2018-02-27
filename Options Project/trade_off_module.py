# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 14:52:06 2018

@author: Alessandro

TRADE-OFF EXPLORATION IN A FORM OF A MODULE

"""

from __future__ import division


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
from helper_module_2 import accepted_maturities
from helper_module import nearest_prev, nearest
import datetime
import itertools


#=============================================================================

put_1_m_limit = 0.95
put_2_m_limit = 0.6

vix_m_limit = 1.2

#============================================================================

def regress(X_test, spx_returns, lin_reg):
    
    #Calculate regression to evaluate vix return with respect to spx return
    # and current market conditions
    y_cap = np.zeros(len(spx_returns))
    counter = 0
    
    #Build grid of VIX returns
    for ret in spx_returns:
        
        X_test['SPX-Return'] = ret
              
        y_cap[counter] = lin_reg.predict(X_test.values.reshape(1, -1))[0]
        
        counter = counter + 1
        
        
    return y_cap

def estimate_carry_and_risk(strike_1, strike_2, strike_vix, price_1, \
                            price_2, price_vix, spx_grid, vix_grid, mult_ratio):
    
    '''
    Parameters:
        
        - Strike_1 is strike of put 1
        - Strike_2 is strike of put 2
        - Strike_vix is strike of vix call
        - price_vix is spot vix
        - spx_grid is grid of potential spx returns
        - vix_grid is grid of potential vix returns
        - mult_ratio is the usual vix options ratio
        
    '''
        
    #Initialize vector of losses
    losses = np.zeros(len(spx_grid))
    
    put_spread_premium = price_1 - price_2
    q = max(round(put_spread_premium * mult_ratio / price_vix),1)
    
    #Compute VIX commissions
    vix_size = 0.7*(price_vix >= 0.1)  \
               +  0.25*(price_vix < 0.05)   \
               +  0.5*(price_vix >= 0.05 and price_vix < 0.1)
                   
    vix_comm = max(1, q*vix_size)  
        
        
    carry = price_1 - price_2 - q*price_vix - 2 - vix_comm
    
    #Now evaluate any scenario to establish risk
    for i in range(0,len(spx_grid)):
    
            #Compute loss for this specific return of spx
            losses[i] = - max(0, strike_1 - spx_grid[i]) \
                        + max(0, strike_2 - spx_grid[i]) \
                        + max(0, vix_grid[i] - strike_vix)
    
    #In the end compute the risk just as the sum of the bad cases
    loss_cases = np.where(losses < 0)[0]       

    
    return carry, sum(loss_cases), q    





def option_selection(data, min_dist, max_dist, mult_ratio):          
                  

    regression_data = pd.read_csv('Regression_dataset.csv')
    
    #Fiter datasets as usual
    df_spx = data[data['underlying_symbol'] == '^SPX']
    df_spx = df_spx[df_spx['option_type'] == 'P']
    df_spx = df_spx[df_spx['trade_volume'] != 0]
    
    
    
    df_vix = data[data['underlying_symbol'] == '^VIX']
    df_vix = df_vix[df_vix['option_type'] == 'C']
    df_vix = df_vix[df_vix['trade_volume'] != 0]
    df_vix = df_vix[df_vix['root'] == ('VIX' or 'VQX')]
    
    spot_date = data['quote_date'][0]
    
    #Filter VIX dataframe on VIX available dates
    ok_maturities = accepted_maturities(df_vix['expiration'].unique(), \
                    datetime.datetime.strptime(spot_date, '%Y-%m-%d'), min_dist, max_dist)
    
    df_vix = df_vix[df_vix['expiration'].isin(ok_maturities)]
    
    #Filter also regression dataset up to today
    try:
        spot_ix = regression_data[regression_data.iloc[:,0] == spot_date].index[0]
        regression_data = regression_data.iloc[:spot_ix,:]
        
    except:
        
        return np.nan, np.nan, np.nan, np.nan
    
    X_train = regression_data.iloc[:-1,1:-1]
    y_train = regression_data.iloc[:-1,-1]
    
    #X for last timestamp (today), the SPX return value will be changed
    X_test = regression_data.iloc[-1,1:-1]
    
    #Prepare Regression
    lin_reg = LinearRegression()
    lin_reg.fit(X_train, y_train)
    
    spx_returns = np.linspace(0.6, 1.6, 100)
    #get_grid out of this
    spot_spx = (df_spx['underlying_bid_1545'].mean() \
                + df_spx['underlying_ask_1545'].mean())/2
                
    spx_grid = spot_spx*spx_returns
    
    vix_returns = regress(X_test, spx_returns, lin_reg)
    
    #get_grid out of this
    spot_vix = (df_vix['underlying_bid_1545'].mean() \
                + df_vix['underlying_ask_1545'].mean())/2
                
    vix_grid = spot_vix*vix_returns
                
    #Get set of maturities for puts
    put_maturities = [datetime.datetime.strptime(x, '%Y-%m-%d') \
                      for x in df_spx['expiration'].unique()]
    
    
    #Filter additionally on strikes requirements
    df_spx = df_spx[df_spx['strike'] <= put_1_m_limit*spot_spx]
    df_spx = df_spx[df_spx['strike'] >= put_2_m_limit**spot_spx]

    df_vix = df_vix[df_vix['strike'] >= vix_m_limit*spot_vix]



    carries = []
    risk = []
    indices_1 = []
    indices_2 = []
    indices_vix = []
    qs = []
    
    

    #Now cycle on any VIX option
    for i in range(0, df_vix.shape[0]):
        
        expiry = df_vix['expiration'].iloc[i]
        
        price_vix = df_vix['ask_1545'].iloc[i]
        strike_vix = df_vix['strike'].iloc[i]
        
        put_expiry = nearest_prev(put_maturities, \
                     datetime.datetime.strptime(expiry, '%Y-%m-%d'))
        
        temp_df = df_spx[df_spx['expiration'] == \
                  datetime.datetime.strftime(put_expiry, '%Y-%m-%d')]
        
        combinations = list(itertools.product(temp_df.index,temp_df.index))
        
        #Now try all the combinations with this VIX option
        for c in combinations:
            
            
            ix_1 = c[0]
            ix_2 = c[1]
            
            if ix_1 == ix_2 or temp_df['strike'][ix_1] < temp_df['strike'][ix_2]:
                           
            
                continue
            
            #Otherwise continuewith the code
            price_1 = temp_df['bid_1545'][ix_1] 
            price_2 = temp_df['ask_1545'][ix_2]
            
            strike_1 = temp_df['strike'][ix_1] 
            strike_2 = temp_df['strike'][ix_2]
            
            carry, ES, q = estimate_carry_and_risk(strike_1, strike_2, strike_vix, \
                           price_1, price_2, price_vix, spx_grid, vix_grid, mult_ratio)
        
            carries.append(carry)
            risk.append(ES)
            
            
            indices_1.append(ix_1)
            indices_2.append(ix_2)
            indices_vix.append(df_vix.index[i])
            qs.append(q)
            
            
           
    
    #Create dataframe with all the combinations, so to read which are the best
    result_df = pd.DataFrame(carries, columns = ['Carry'])
    result_df['Risk'] = risk
    result_df['Trade-off'] = result_df['Carry']/abs(result_df['Risk'])
             
    
    #Filter combinations with negative carry
    result_df = result_df[result_df['Carry'] > 0]
    
    #If the shape of the dataframe is 0, then there are no feasible combinations
    if result_df.shape[0] == 0:
        
        return np.nan, np.nan, np.nan, np.nan
    
    #Sort combinations based on this trade-off measure and choose the best
    result_df.sort_values('Trade-off', inplace = True, ascending = False)
    combination_ix = result_df['Trade-off'].idxmax()

    
    #Return the position in the dataframe for each option and q
    return indices_1[combination_ix], indices_2[combination_ix], \
           indices_vix[combination_ix], qs[combination_ix]
    