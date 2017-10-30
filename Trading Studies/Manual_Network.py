#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 20:55:13 2017

@author: ale

Manually creates network with matrix calculation
Network is initialized with random weights

FOR THE MOMENT N IS FIXED TO 3

Network matrix (NxM) represent weights :
    N (number of elements left layer) 
    M (number of elements right layer) 
    
"""
import numpy as np


class my_network():

#    IF I WANT TO INIITIALIZE FROM SRATCH
#    def __init__(self, layer_sizes, sigma = 1):
#        
#        #Initialize network
#        self.n = len(layer_sizes)
#        
#        
#        self.L1 = np.random.randn(layer_sizes[0],layer_sizes[1])
#        self.L2 = np.random.randn(layer_sizes[1],layer_sizes[2])
#        self.L3 = np.random.randn(layer_sizes[2],1)
        
#    IF I WANT TO INIITIALIZE IN OTHER CODE
    def __init__(self, M1, M2, M3):
        
        #Initialize network
        self.L1 = M1
        self.L2 = M2
        self.L3 = M3
        
        #Check sizes and complain if something is wrong
        if(M1.shape[1] != M2.shape[0]):
            print('Layer 1 dimensions not matching')
        if(M2.shape[1] != M3.shape[0]):
            print('Layer 2 dimensions not matching')
        if(M3.shape[1] != 1):
            print('Last matrix is not a vector!')   
    
    #Modifies layer nodes with noise
         
    def evaluate(self,X,y_true, threshold = 0.5):     
        #RETURNS ACCURACY OF PREDICTION
        #y_true is pd.Series
        
        
        N = X.shape[0]
        
        if(N != y_true.shape[0]):
            
            print('Dimension Error')
            return 0
        
        
        y_cap = np.zeros(N)
        
        for i in range(0,N):
            
            out_1 = np.dot(X.iloc[i,:].values, self.L1)  
        
            #GO THROUGH RELU
            out_1 = out_1*(out_1 > 0)
        
            out_2 = np.dot(out_1, self.L2) 
            
            #GO THROUGH RELU
            out_2 = out_2*(out_2 > 0)
        
            out_3 = np.dot(out_2, self.L3)
            
            y_cap[i] = 1/(1+np.exp(out_3))[0]
        
        y_cap = 1*(y_cap > threshold)
        
        acc = sum(1*(y_true.values == y_cap))/N
        
        return round(acc,4)
    
    def predict(self,X,threshold = 0.5):     
        #RETURNS ACCURACY OF PREDICTION
        #y_true is pd.Series
        
        
        N = X.shape[0]
        

        y_cap = np.zeros(N)
        
        #Convert to numpy so it will be faster
        Z = X.values
        
        for i in range(0,N):
            
            #out_1 = np.dot(X.iloc[i,:].values, self.L1)  
            out_1 = np.dot(Z[i,:], self.L1)  
            
            #GO THROUGH RELU
            out_1 = out_1*(out_1 > 0)
        
            out_2 = np.dot(out_1, self.L2) 
            
            #GO THROUGH RELU
            out_2 = out_2*(out_2 > 0)
        
            out_3 = np.dot(out_2, self.L3)
            
            y_cap[i] = 1/(1+np.exp(out_3))[0]
        
        return 1*(y_cap > threshold)
            
        

