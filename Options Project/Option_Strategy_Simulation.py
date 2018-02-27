# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 14:33:52 2018

@author: Alessandro

OPTION SIMULATION WITH DAILY TRADE-OFF ANALYSIS

Every day the combination is changed based on the outcome of
the trade-off analysis (carry/risk profile)

Remember Conventions:
    
    - Option 1 is the spx put option we sell
    - Option 2 is the spx put option we buy
    - Option vix refers to the vix call(s) we buy
    
    
Further improvements:

    - Make the mult_ratio parameter dynamic (around 0.5 anyway)
    - Consider liquidating the position if spikes from the VIX are higher
      than those expected by the model
    - Consider trading several option combinations each day to diversify more
    - Better estimation of risk (at the moment it's just sum of negative scenarios)
    
    
    
All files should be extracted in the folder ~script path\\CBOEOptionsData\\   
 
"""

import pandas as pd
import os
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from helper_module import daily_pnl_calc
from helper_module import nearest_couple
from helper_module import nearest
from helper_module import locate_maturity
from trade_off_module import option_selection



plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
                'ytick.color':'green','grid.color':'grey', 'xtick.color':'green',\
                'figure.facecolor':'black', 'figure.edgecolor':'green', 
                'grid.linestyle':'--'})


#VIX EXISTS FROM 2006-02-27

#PARAMS
#=======================================================================

#Ideal trading window
N_days = 90

#Range of expiration days where to look for options
max_date = 120
min_date = 60

#for each dollar coming from the put spread
#how much is invested in VIX options
#This needs to be made dynamically changing!
mult_ratio = 0.5
            
#Start and end days (fixed to be compared with Carlo's results)
inizio = 457
fine = 2389

#=======================================================================

#ALL FILES SHOULD BE EXTRACTED TO A FOLDER \\CBOEOptionsData\\
fPath = os.path.dirname(os.path.abspath(__file__)) + '\\CBOEOptionsData\\'

#List of files in folder
files = [x for x in os.listdir(fPath)]

#List of available days for trading
dates_list = [x[26:36] for x in files]

#List of available days for trading in datetime format
file_dates = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in dates_list]

#For pplotting purposes
x_ticks = [x[26:33] for x in files[inizio:fine]]

premiums = np.zeros(len(files))
payoffs = np.zeros(len(files))
snp = np.zeros(len(files))
vix = np.zeros(len(files))
option_sell = np.zeros(len(files))
date_diff = np.zeros(len(files))
payoff_for_comps = np.zeros(len(files))
daily_pnl = np.zeros(len(files))

#Array that contains only the pnl from the vix option, to see how it hedges
vix_check = np.zeros(len(files))


counter = 0

start = time.time()

#Load data only of not already stored in memory
if 'data' not in globals():
    
    print '\nLoading Data...\n'
    
    #Initialize dictionary of dataframes
    data = dict()

    for f in files:
        
        data[f] = pd.read_csv(fPath + f)
    
    
    print 'Done in', time.time() - start

print '\nSimulating...\n'



for f in tqdm(files[inizio:fine]):
  
    df = data[f]
    df_vix = df
    
    #Careful if close to end of files don't trade
    if counter >= len(files) - N_days:
        
        counter = counter + 1
        continue
    
    #Store spot vix and spx
    snp[counter] = (df['underlying_bid_1545'].iloc[0] \
                    + df['underlying_bid_1545'].iloc[0])/2

    vix[counter] = df_vix['active_underlying_price_1545'].iloc[-1] 
    
    #Get the indices of options to be traded and the number of lots of vix options (q)
    #Parameters are the daily dataframe, the range of time where to look for maturitues
    # and at last the vix option ratio           
    ix_1, ix_2, ix_vix, q = option_selection(df, min_date, max_date, mult_ratio)  
    
    #Sometimes no combination satisfies the requirements
    if np.isnan(ix_1):
        
        counter = counter + 1
        continue
    
    #Get expiry data to compute pnl
    chosen_exp = df['expiration'][ix_1]
    chosen_exp_vix = df['expiration'][ix_vix]

    chosen_str_1 = df['strike'][ix_1]
    chosen_str_2 = df['strike'][ix_2]
    chosen_str_vix = df['strike'][ix_vix]                 
    
    
    #Locate file where last trading data is available  
    maturity_date = locate_maturity(data,  \
                    datetime.datetime.strptime(chosen_exp, '%Y-%m-%d')) 
    maturity_date_vix = locate_maturity(data,  \
                    datetime.datetime.strptime(chosen_exp_vix, '%Y-%m-%d'))
  
    
    
    
    ######################################################################
    #                                                                    #
    #                        COMPUTING PAYOFFS                           #
    #                                                                    #
    ######################################################################
        
    
    #Consider Hedge ratio
    put_spread_premium = df['bid_1545'][ix_1] - df['ask_1545'][ix_2]
    vix_premium = df_vix['ask_1545'][ix_vix]

    #Now add commission    
    put_spread_premium = put_spread_premium - 2
   
    #Put payoff at the right index    
    #Vix options are liquidated at the matuirty of the put spread
    payoff_index = files.index('UnderlyingOptionsEODCalcs_' + maturity_date + '.csv')
    
    
    #Get which index in file_list is today and expiry, to cycle between them
    oggi = files.index(f)
    
    #Compute value of put portfolio along its life
    position_pnl = daily_pnl_calc(data, files, oggi, payoff_index, chosen_exp, \
                   chosen_str_1, chosen_str_2, put_spread_premium, q,'^SPX')
                                         
                       
    position_pnl_vix = daily_pnl_calc(data, files, oggi, payoff_index, chosen_exp_vix, \
                       chosen_str_vix, 0 , -vix_premium, q, '^VIX')               
                    
               
               
    daily_pnl = daily_pnl + position_pnl + position_pnl_vix  
    
    vix_check = vix_check + position_pnl_vix  

    counter = counter + 1
 
#%%    
#=============================================================================

#Report PnL
start_cap = 100000

#Add starting capital to give sense to returns
daily_pnl = daily_pnl + start_cap

#Compute daily returns
daily_ret = daily_pnl/np.roll(daily_pnl,1) - 1
daily_ret[0] = 0

#Save PnL to excel
pnl_df = pd.DataFrame(pd.to_datetime(dates_list), columns = ['Date'])
pnl_df['Daily_Return'] = daily_ret

pnl_df.to_excel('Option_PnL.xlsx')

#%%
#=============================================================================
#Plot Pnl line and underlyings

#Frequency of x-ticks on graph
tick_freq = 250

#If there isa figure plot on it 
if 'fig' not in globals():
    
    fig = plt.figure()

    plt.title('Analysis')    
    
    

ax1 = plt.subplot(2,1,1)
ax1.set_title('Equity Line', color = 'green')
#ax2.plot(e_line)
ax1.plot(daily_pnl[inizio:fine])

#ax4 = ax1.twinx()
#ax4.plot(u_curve[inizio:fine], 'r-')
#ax4.tick_params('y', colors='green')


plt.grid(True)
plt.autoscale(enable=True, axis='x', tight=True)

plt.xticks(np.arange(len(x_ticks[0::tick_freq]))*tick_freq, \
           x_ticks[0::tick_freq], rotation = 45)

#++++++++++++++++++++++++++++++++++++++++++
           
ax2 = plt.subplot(2,1,2)
ax2.set_title("Underlying", color = 'green')
ax2.plot(snp[:fine - inizio])
ax2.tick_params('y', colors='green')

ax3 = ax2.twinx()
ax3.plot(vix[:fine - inizio], 'r-')
ax3.tick_params('y', colors='green')

plt.grid(True)
plt.autoscale(enable=True, axis='x', tight=True)

plt.xticks(np.arange(len(x_ticks[0::tick_freq]))*tick_freq, \
           x_ticks[0::tick_freq], rotation = 45)
           
           
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++

           
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()