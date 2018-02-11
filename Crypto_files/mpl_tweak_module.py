# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 14:13:03 2018

@author: Alessandro-Temp

MODULE FOR MATPLOTLIB CUSTOMIZATION

"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

#DEFINE GLOBAL FEATURES

rc_dict = \
{'axes.edgecolor':'green', \
 'axes.facecolor':'black', \
 'ytick.color':'green',  \
 'xtick.color':'green',  \
 'grid.color':'grey',    \
 'grid.linestyle':'--',  \
 'grid.linewidth': 0.4,    \
 'figure.facecolor':'black' \
 }

#Keep dictionary of default features


def set_params():
    
    for x in rc_dict:
    
        mpl.rcParams[x] = rc_dict[x]
    
    return 0



def reset():
    
    for x in rc_dict:
        
        mpl.rcParams[x] = rc_dict[x]

    
    