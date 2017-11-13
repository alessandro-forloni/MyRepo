'''

=================================

- Read TestData.csv
- Set a threshold
- Compute returns (for simplicity only on Bid or Ask)

=================================

'''
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

class Filter():

    
    def __init__(self, df, thresh):
        
        #df must  be the ready-to-use series
        
        self.threshold = thresh
        self.df = df
        self.out = np.zeros(df.shape[0])
        
        
     
    ##################################################################
    ##################################################################
    
    '''
    
    Core class that does all the job of discretizing the series.
    In addition, it computes average long and short overshoot.
    
    '''
    
    def Discretize(self):  
        
        
        #Measure elapsed time after having read the file
        start = time.time() 
         
        #%%
        
        #Core array that stores price levels at intrinsic times        
        price_levels = np.zeros(self.df.shape[0])
        vec = self.df.values
        
        #To compute statistics
        up_overshoot = np.zeros(self.df.shape[0])
        down_overshoot = np.zeros(self.df.shape[0])
        
        up_counter = 0
        remember_up = 0
        
        down_counter = 0
        remember_down = 0
        #For Graphic purposes
        price_levels[0] = vec[0] 
        
        #Start by default from up
        mode = 'up'
        curr_max = self.df[0]
        curr_min = self.df[0]
        
        #Indices of highs and lows
        curr_max_ix = 0
        curr_min_ix = 0
        
        #Cycle through the whole series        
        for i in range(0,self.df.shape[0]):
            
            #Triggers for a new downward/upward phase
            low_trigger = curr_max*(1-self.threshold/100)
            high_trigger = curr_min*(1+self.threshold/100)
            
            #Up mode
            if mode == 'up':
                
                if(vec[i] >= curr_max):
                    
                    curr_max = vec[i]
                    curr_max_ix = i
                    
                    
                elif(vec[i] <= low_trigger):
                    
                    #If intrinsic event threshold is triggered
                    
                    # Register previous level price to compute overshoot
                    prev = price_levels[remember_up]
                    
                    # Register new_level
                    price_levels[i] = low_trigger
                    # Register last max
                    price_levels[curr_max_ix] = vec[curr_max_ix]
                    
                    #Compute overshoot
                    up_overshoot[up_counter] = (curr_max - prev)/prev
                    up_counter = up_counter + 1 
                    
                    #Switch mode to 'down'
                    mode = 'down'
                    curr_max = 0
                    
                    #To see which price level to take for down overshoot
                    remember_down = i
                    
                    
            elif (mode == 'down'):
                
                if(vec[i] <= curr_min):
                    
                    curr_min = vec[i]
                    curr_min_ix = i
                    
                    
                #Directional Change
                elif(vec[i] >= high_trigger):
                
                    # Register previous level price to compute overshoot
                    prev = price_levels[remember_down]
                    
                    
                    price_levels[i] = high_trigger
                    price_levels[curr_min_ix] = vec[curr_min_ix]
                    
                    #Compute overshoot
                    down_overshoot[down_counter] = (curr_min - prev)/prev
                    down_counter = down_counter + 1 
                    
                    #Switch mode to 'up'
                    mode = 'up'
                    curr_min = 1e5
                    
                    remember_up = i
                    
               
            
        #Just for graphic purposes    
        price_levels[-1] = vec[-1]    
        
        self.out = price_levels
        
        #Output data in a meaningful way
        ix = np.where(price_levels != 0)[0]
        
        final_df = pd.DataFrame(price_levels[price_levels != 0], index = ix)
        final_df.columns = ['Intrinsic Level']
        
        #Print Elapsed time and statistics
        print('\n==============================================')
        print('Threshold:', self.threshold, '%') 
        print('\nExecution time:', round(time.time() - start,2), 'Seconds')
         
        print('Average Long Overshoot: ', 
              round(np.mean(up_overshoot[:up_counter-1])*100,4),'%')
        
        print('Average Short Overshoot: ', 
              round(np.mean(down_overshoot[:down_counter-1])*100,4),'%')
        
        return final_df
    
    
    
    ##################################################################
    ##################################################################
    
    
    def visualize(self, ax, N):
            
        #Plot only the first N occurrences
        #ax is the axis object to plot on
        
        #Plot only prices that have been registered
        x = np.where(self.out[:N] != 0)[0]
        y = self.out[:N][self.out[:N] != 0]
        
        # Just for graphic purposes
        # Append last price to thediscretized set
        x = np.append(x, N)
        y = np.append(y, self.df[N])   
        
        #fig = plt.figure()
        #ax = fig.add_subplot(111)
        
        ax.plot(self.df[:N])
        ax.plot(x, y, 'r*-')
        #ax.plot(N, self.df[N], 'r*-')
        ax.set_title('Threshold ' + str(self.threshold) + '%')
        
        return ax
        
        
                    
                    
                    
               
            
       