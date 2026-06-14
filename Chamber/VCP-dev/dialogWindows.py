# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 16:18:33 2024

@author: ROWANJ2
"""

import tkinter as tk
from tkinter import ttk as ttk



class calibWindow(tk.Toplevel):

    def __init__(self, parent, calibrateCommand ):
        # super().__init__(self, parent)
        # self.top = tk.Toplevel(parent)
        tk.Toplevel.__init__(self, parent)


        self.columnconfigure( index=0, weight=1 )
        self.rowconfigure( index=0, weight=1 )
        self.title = "MC Calibration"
        self.initWidgets(calibrateCommand)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        # print( "+%d+%d" % (parent.winfo_rootx()+450, parent.winfo_rooty()+250) )
        self.geometry( "350x250+500+300" )
        
    def initWidgets(self, calibrateCommand):
        self.frame = ttk.Frame(self)
        self.frame.grid(row = 0, column = 0, sticky = 'nesw')
        self.frame.rowconfigure( index=0, weight=2 )
        self.frame.rowconfigure( index=1, weight=1 )
        self.frame.rowconfigure( index=2, weight=1 )
        
        self.lblTitle = ttk.Label(self.frame, text="Calibration Verifcation", style = 'Header.TLabel')
        self.lblTitle.grid( row = 0, column = 0, columnspan = 2, sticky='ew' )
        self.lblLabel = ttk.Label(self.frame, text="Ensure needle is straight up (at 0°)\nand centered on chamber", style = 'Std.TLabel')
        self.lblLabel.grid( row = 1, column = 0, columnspan = 2, sticky = 'ew')

        self.btDoCalibration = ttk.Button(self.frame, text="Good", command=calibrateCommand, style = 'Std.TButton')
        self.btCancel = ttk.Button(self.frame, text="Cancel", command=self.cancel, style = 'Std.TButton')
        
        self.btDoCalibration.grid(row = 2, column = 0)
        self.btCancel.grid(row = 2, column = 1)

    def ok(self):
        # print( "value is", self.e.get() )
        print("Pressed Okay")
        self.destroy()
        
    def cancel(self):
        self.destroy()