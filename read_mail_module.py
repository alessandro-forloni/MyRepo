#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 11:17:32 2018

@author: alessandro

READ_MAIL IN A FORM OF MODULE

RETURNS TWO LISTS OF CRYPTOS, A LIST OF EXCHANGES AND A LIST OF POSITIONS
 
"""

import imaplib
from bs4 import BeautifulSoup

action_dict = {'buy' : 1 , 'sell' : -1}

## Connect to imap server
username = 'alessandro.forloni@nafora.ch'
password = ######

def fetch_arbs():
    
    mail = imaplib.IMAP4_SSL('outlook.office365.com')
    mail.login(username, password)
    mail.select("Crypto")
    
    
    #retrieve a list of the UIDs for all of the messages in the select mailbox
    result, numbers = mail.uid('search', None, 'ALL')
    uids = numbers[0].split()
    
    result, messages =mail.uid('fetch', ','.join(uids[-10:]), "(UID BODY[TEXT])")
        
    #Check only last message
    messaggio = messages[-2][1]
    
    soup = BeautifulSoup(messaggio, 'html.parser')
    
    #Enter the table
    table = soup.find_all('table')
    
    #Search all the arbitrages in the table
    arbs = table[0].find_all('tr')
    
    #arbs[0] is always the header of the table, so start from one
    for i in range(1,len(arbs)):
    
        crypto_1 = []
        crypto_2 = []
        
        #Compacted text
        texts = [x.text.strip() for x in arbs[i].find_all('td')]
        
        #We care about elements in positions (4,5,6,8,9,10,12,13,14) the last three are for three pair arb
        exchanges = [texts[4], texts[8], texts[12]]
        pairs_raw = [texts[5], texts[9], texts[13]]
        actions_raw = [texts[6], texts[10], texts[14]]
        
    
        #Check and clean arbitrages
        
        #error in formatting or something
        if(exchanges[0] == '-'):
            
            continue
        
        #It's a two pair arb and not three
        if(exchanges[2] == '-'):
            
            del exchanges[-1]
            del pairs_raw[-1]
            del actions_raw[-1]
        
        #Process Pairs
        for j in range(0, len(pairs_raw)):
            
            pair = pairs_raw[j].split("/")
            
            crypto_1.append(pair[0])
            crypto_2.append(pair[1])
            
            
#        print '\nArbitrage', i
#        
#        print exchanges
#        print crypto_1
#        print crypto_2
#        print map(action_dict.get, actions_raw)
    
        actions = map(action_dict.get, actions_raw) 
        
        
        #Return only first arbitrage
        return exchanges, crypto_1, crypto_2, actions
    

    #If not entering the cycle just return 4 empty lists
    return [],[],[],[]

