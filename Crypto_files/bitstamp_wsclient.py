# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 18:47:08 2018

@author: Alessandro-Temp

WEBSOCKET TRY

"""
import wsclient

client = wsclient.BitstampWebsocketClient()
client.subscribe("live_trades", "btc", "eur")
