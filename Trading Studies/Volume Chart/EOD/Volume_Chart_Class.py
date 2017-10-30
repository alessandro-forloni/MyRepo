"""
=========================================================
Volume distribution chart given usual dataframe of prices
=========================================================


"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#Basic Cross Ball plot
plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', 'ytick.color':'green','xtick.color':'green','grid.color':'grey', 'grid.linestyle':'--'})

class Charter():
    
    #Initialize class with data and window
    def __init__(self, df, p=5):
        
        self.data = df
        self.window = p


    def plot(self):
        
        #Convert datetimes to simple strings
        self.data['Date'] = self.data['Date'].apply(lambda x: str(x)[:10])
        
        days = self.data['Date'].unique()
        
        dz = dict()
        
        for d in days[-self.window:]:
            
            df = self.data[self.data['Date'] == d]
            dz[d] = df.groupby('Close').sum()['Vol']
            
        
        
        #Plot now, day by day
        
        #Set left offsets
        space = 200/self.window
        lefts = np.arange(0,self.window)*space
        count = 0
        width_par = 10*self.window
        
        fig, ax = plt.subplots()
        
        for d in days[-self.window:]:
            
            ax.barh(dz[d].index, dz[d].values/width_par, height=5, left=lefts[count])
            count = count+1
            
        ax.set_xticks(lefts)
        ax.set_xticklabels(days[-self.window:])
        plt.xticks(rotation = 45 )
        
        ax.set_ylabel("Data values")
        ax.set_xlabel("Data sets")
        
        #ax.grid(True)
        ax.set_title('Volume Distribution Plot', color = 'g')
        
        fig.patch.set_facecolor('black')
        fig.patch.set_edgecolor('green')
        
        plt.show()    
            
    
    
