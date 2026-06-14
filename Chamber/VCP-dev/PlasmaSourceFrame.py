import tkinter as tk
from tkinter import ttk as ttk
from BKPrecisionFrame import BKP9115Frame
from HeatFrame import HeatFrame
from BiasFrame import BiasFrame
from VCP_GUI_Elements import DataEntry

class PlasmaSourceFrame( ttk.Frame ):
    #Constructor
    def __init__(self, parent):
        super().__init__(parent)
        self.names = [ 'heat1', 'heat2', 'bias' ]
        
        self.frHeat1 = HeatFrame( self, "Heat 1" )#names[0], COMList[0], btConnect[0], btOutput[0],\
                                    #btSetInput[0], ltCOM[0], ltOutput[0], enInput[0] )
        self.frHeat2 = HeatFrame( self, "Heat 2" ) #names[1], COMList[1], btConnect[1], btOutput[1],\
                                    #btSetInput[1], ltCOM[1], ltOutput[1], enInput[1] )
        self.frBias = BiasFrame(self, "Bias" ) #names[2], COMList[2], btConnect[2], btOutput[2],\
                                    #btSetInput[2], ltCOM[2], ltOutput[2], enInput[2] )
        
        # try:
        #     self.grid_propagate(0)
        #     self['width'] = 400
        #     # print('winfo hieght is ', parent.winfo_screenheight())
        #     self['height'] = 1000
        # except:
        #     print("broke defining height")
        self['borderwidth'] = 1
        self['relief'] = 'solid'
        # self.geometry( "500x500" )
        self.initLocations()
            
        # self.initWidgets()
    def initWidgets(self):
        self.frHeat1.initWidgets()
        self.frHeat2.initWidgets()
        self.frBias.initWidgets()
        
        self.frHeat1.listRamp.setSelection('30min')
        self.frHeat2.listRamp.setSelection('30min')
        self.frBias.listRamp.setSelection('1min')
        
        # self.frHeat1.setFilamnetNumber(3)
        # self.frHeat2.setFilamnetNumber(4)

        
    def updateWidgets(self, ports, portStatus, outputStatus, setpoint, v, i, q, T, autoMode):
        
        # print("updateWidgets() method called from PlasmaSourceFrame")
        self.frHeat1.updateWidgets( ports, portStatus[0], outputStatus[0], setpoint['heat1'], v['heat1'], i['heat1'], q['heat1'], T['heat1'], autoMode )
        self.frHeat2.updateWidgets( ports, portStatus[1], outputStatus[1], setpoint['heat2'], v['heat2'], i['heat2'], q['heat2'], T['heat2'], autoMode )
        self.frBias.updateWidgets( ports, portStatus[2], outputStatus[2], setpoint['bias'], v['bias'], i['bias'], autoMode )
        
    def initLocations(self):
        self.columnconfigure( index=0, weight=0 )
        self.rowconfigure( index=1, weight=1 )
        self.rowconfigure( index=2, weight=1 )
        self.rowconfigure( index=3, weight=1 )
        
        self.lblTitle = ttk.Label(self, text = 'Plasma Sources', style = 'Header.TLabel')
        self.lblTitle.grid( row=0, column=0 )
        
        # self.frHeat1.initWidgets()
        self.frHeat1.grid( row = 1, column = 0, sticky = 'nsew' )
        self.frHeat2.grid( row = 2, column = 0, sticky = ' nsew' )
        self.frBias.grid( row = 3, column = 0, sticky = ' nsew' )
        