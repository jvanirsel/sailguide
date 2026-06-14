# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 17:31:27 2024

@author: ROWANJ2
"""

import tkinter as tk
import tkinter.ttk as ttk
from VCP_GUI_Elements import *

class PNIFrame( ttk.Frame ):
    def __init__(self, parent):
        super().__init__(parent)
        self['borderwidth'] = 1
        self['relief'] = 'solid'
    
    def updateWidgets(self, ports, portStatus, outputStatus, autoMode, dvMagField ):
        self.btConnect.updateStatus( portStatus )
        self.ltCOM.updateStatus( portStatus )
        self.listCOM.updateStatus( portStatus, ports )
        if portStatus == 1:
            # self.btOutput.updateStatus( 1 )
            self.btPollData.updateStatus( outputStatus )
            self.ltActive.updateStatus( outputStatus )# to add sample light IH
            # print("Data is ", dvMagField)
            self.BxData.setData(dvMagField['Bx'] ) # JR change
            self.ByData.setData(dvMagField['By'] ) # JR change
            self.BzData.setData(dvMagField['Bz'] ) # JR change
            
        else:
            self.btPollData.updateStatus( 0 )
            
        if autoMode == 1:
            self.btPollData.updateStatus( 0 )
            
    def initWidgets(self):
        print("initWidgets() method called for PNIFrame")
        self.frCOM = ttk.Frame(self)
        self.frParams = ttk.Frame(self)
        self.frData = ttk.Frame(self)
        
        self.listCOM = PortSelectorBox( self.frCOM, 'PNI' )
        self.btConnect = ConnectButton( self.frCOM, 'PNIconnect' )
        self.ltCOM = StatusLight( self.frCOM, 'PNIcom' )
        self.ltActive = StatusLight( self.frCOM, 'PNIactive' )
        
        
        self.BxData = DataEntry(self.frData, 'Test Data', False, 8) # IH change
        self.ByData = DataEntry(self.frData, 'Test Data', False, 8) # IH change
        self.BzData = DataEntry(self.frData, 'Test Data', False, 8) # IH change
        self.BxData.setData('-1') # IH change
        self.ByData.setData('-2') # IH change
        self.BzData.setData('-3') # IH change
        
        self.btPollData = PushButton(self, 'PNIpoll')
        # self.ltActive = StatusLight( self.frCOM, 'WSLPoutput' )
        
        self.initLabels()
        self.initLocations()

        
        
    def initLabels(self):
        self.lblTitle = ttk.Label(self, text = 'PNI', style = 'Header.TLabel' )
        self.lblCOMPort = ttk.Label( self.frCOM, text = 'COM Port:', style = 'Std.TLabel' )
        self.lblCOMStatus = ttk.Label( self.frCOM, text = 'COM Status', style = 'Std.TLabel' )
        self.lblBx = ttk.Label(self.frData, text = 'Bx', style = 'Std.TLabel') # IH change
        self.lblBy = ttk.Label(self.frData, text = 'By', style = 'Std.TLabel') # IH change
        self.lblBz = ttk.Label(self.frData, text = 'Bz', style = 'Std.TLabel') # IH change
        self.lblmicroTx = ttk.Label(self.frData, text = 'microT', style = 'Std.TLabel') # IH change
        self.lblmicroTy = ttk.Label(self.frData, text = 'microT', style = 'Std.TLabel') # IH change
        self.lblmicroTz = ttk.Label(self.frData, text = 'microT', style = 'Std.TLabel') # IH change
        # self.lblOutput = ttk.Label( self.frCOM, text = 'Sweeping', style = 'Std.TLabel' )
        
    def initLocations(self):
        print("initializing widgets & placement for PNI frame" )
        self.columnconfigure( index=0, weight=0 )
        # self.columnconfigure( index=1, weight=0 )
        # self.columnconfigure( index=2, weight=0 )
        self.rowconfigure( index=0, weight=0 )
        # self.rowconfigure( index=1, weight=1) # IH change
        # self.rowconfigure( index=2, weight=1)
        # self.rowconfigure( index=3, weight=1)
        # self.rowconfigure( index=4, weight=1)
        # self.rowconfigure( index=5, weight=1)
        # self.rowconfigure( index=6, weight=5)
        self['padding'] = ('0.1c', '0.1c')
        
        self.lblTitle.grid( row = 0, column = 0, columnspan = 2 )
        
        self.frCOM.columnconfigure(index=2, weight=1)
        # self.frCOM.rowconfigure(index=0, weight=1)
        self.frCOM['padding'] = ('0.1c', '0.25c')
        # self.frCOM['relief'] = 'sunken'
        self.frCOM.grid( row = 1, column = 0, columnspan = 2, sticky = ' ew' )
        self.lblCOMPort.grid( row = 0, column = 1)
        self.listCOM.grid( row = 0, column = 2 )
        self.btConnect.grid( row = 1, column = 2)#, padx = 10 )
        self.ltCOM.grid( row = 1, column = 0 )
        self.lblCOMStatus.grid( row = 1, column = 1)
        
        self.frData.grid( row = 2, column = 0, columnspan = 3)
        self.lblBx.grid(row = 0, column = 0) # IH change
        self.BxData.grid( row = 0, column = 1) # IH change
        self.lblmicroTx.grid(row = 0, column = 2) # IH change
        self.lblBy.grid(row = 1, column = 0) # IH change
        self.ByData.grid( row = 1, column = 1) # IH change
        self.lblmicroTy.grid(row = 1, column = 2) # IH change
        self.lblBz.grid(row = 2, column = 0) # IH change
        self.BzData.grid( row = 2, column = 1) # IH change
        self.lblmicroTz.grid(row = 2, column = 2) # IH change
        self.btPollData.grid(row = 3, column = 0) # IH change
        # self.lblOutput.grid( row = 1, column = 3)
        # self.ltActive.grid( row = 1, column = 4)