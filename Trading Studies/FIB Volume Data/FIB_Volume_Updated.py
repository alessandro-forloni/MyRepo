import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation



#Basic Cross Ball plot
plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', 'ytick.color':'green','grid.color':'grey', 'grid.linestyle':'--'})
#plt.ion()    

#Threshold for Volume representation
Threshold = 150

#Threshold for book escape measure
b_threshold = 50

def load_n_plot(ss, Sheetname = 'Sheet1'):
    
    Data_Size = 800
    
    df = pd.read_excel(ss, sheetname = Sheetname).iloc[-Data_Size:,:]
    #df = pd.read_excel(ss, sheetname = Sheetname).iloc[4650:,:]
    
    
    #Clean volume data from extra large orders
    #cap_indexes = df[df['Volume'] > Threshold].index
    #df.loc[cap_indexes ,'Volume'] = 1#Threshold
          
    #volume stuff
    vol_side = np.zeros(df.shape[0])
    df['Vol_Power'] = df['Volume']*(df['B/A']=='A') - df['Volume']*(df['B/A']=='B')
    
    #Book calculation
    df['Bid_Sum'] = df['Bid_1'] + df['Bid_2'] #+ df['Bid_3'] + df['Bid_4'] + df['Bid_5'] 
    df['Ask_Sum'] = df['Ask_1'] + df['Ask_2'] #+ df['Ask_3'] + df['Ask_4'] + df['Ask_5'] 
    
    
    
    #Check Bid Escape 
    df['Bid_Delta'] = df['Bid_Sum'] < df['Bid_Sum'].shift(1) - b_threshold
    #Check Ask Escape 
    df['Ask_Delta'] = df['Ask_Sum'] < df['Ask_Sum'].shift(1) - b_threshold
      
      
    i = 0
    
    for index,row in df.iterrows():
    
        #PROVA UN CUMSUUUUUUUUUUUM
        vol_side[i] = df['Vol_Power'][:i].sum() #[:index].sum()
        i = i+1
      
    df['Vol_Side'] = vol_side
      
    return df


fig = plt.figure()
ax1 = fig.add_subplot(211)
plt.grid(True)
ax2 = fig.add_subplot(212)
fig.show()
plt.grid(True)
fig.patch.set_facecolor('black')
fig.patch.set_edgecolor('green')


while len(plt.get_fignums()) != 0: 
    
    df = load_n_plot('data-19-10.xlsx', Sheetname = 'data-19-10') 
    y = df['Price']
    v = df['Vol_Side']
    x = y.index.values
    
    #Select values based on vol side
    a_index = df[df['B/A'] == 'A'].index
    b_index = df[df['B/A'] == 'B'].index
    x_index = df[df['B/A'] == 'X'].index
           
    #Did anybody escape from the Ask?            
    #u_index = df[df['Ask_Delta'] == True].index 
    #Did anybody escape from the Bid?            
    #d_index = df[df['Bid_Delta'] == True].index             
 
    #Plot the three series
    ax1.plot(a_index,y[a_index], 'b^')
    ax1.plot(b_index,y[b_index], 'rx')
    ax1.plot(x_index,y[x_index], 'go')
    
    #Plot Book escape data
    #ax1.plot(u_index,y[u_index] + 10, 'wv')
    #ax1.plot(d_index,y[d_index] - 10, 'y^')

    
    fig.canvas.draw()
    
    offset = 30 #df['Bid_Sum'].iloc[0]
    ax2.cla()
    #ax2.plot(x,df['Bid_Sum']-offset, 'g-')
    #ax2.plot(x,df['Ask_Sum']-offset, 'r-')
    #ax2.plot(x,df['Bid_1']-offset, 'g-')
    #ax2.plot(x,df['Ask_1']-offset, 'r-')
    ax2.plot(x,v, 'w-')
    ax2.plot(x,df['Volume'], 'g+')
    
    
    fig.canvas.draw()
    plt.grid(True)
    plt.pause(1)
    
        