"""
=========================================================
Volume distribution chart given usual dataframe of prices
=========================================================

With Cool Input!

"""

#from tkinter import *
import tkinter as tk
import pandas as pd
import Volume_Chart_Class

fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'

if 'data' not in locals():
    data = pd.read_excel(fName, Sheetname = '1M')

def show_entry_fields():
   
   global n
   n = e1.get()
   master.destroy()
   
   chart = Volume_Chart_Class.Charter(data, int(n))
   chart.plot()
     

master = tk.Tk()
# width x height + x_offset + y_offset:
master.geometry("200x50+100+100") 

tk.Label(master, text="N_Days",bg="red", fg="white").grid(row=0)

tk.Button(master, text='OK', command=show_entry_fields).grid(row=3, column=1, sticky='W', pady=4)

e1 = tk.Entry(master)
e1.place(x = 50, y = 50)
e1.grid(row=0, column=1)

tk.mainloop( )



