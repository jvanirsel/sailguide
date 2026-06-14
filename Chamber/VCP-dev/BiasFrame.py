import tkinter as tk
import tkinter.ttk as ttk
import scipy.optimize as sp
from VCP_GUI_Elements import *
from BKPrecisionFrame import BKP9115Frame

class BiasFrame( BKP9115Frame ):
    def __init__(self, parent, name):
        super().__init__(parent, name)
    
    def initWidgets(self): # calls all subsequent methods
        print("Widgets being made for " + self.name)
        self.frCOM = ttk.Frame(self)
        self.frData = ttk.Frame(self)
        self.listCOM = PortSelectorBox( self.frCOM, self.name )
        self.listRamp = RampTimeBox( self.frData, self.name )
        self.btConnect = ConnectButton( self.frCOM, self.name+'connect' )
        self.btOutput =  PushButton( self.frData, self.name + 'active')
        self.btSetInput = ClickButton( self.frData, self.name+'set') 
        self.ltCOM = StatusLight( self.frCOM, self.name + 'com' )
        self.ltActive = StatusLight( self.frCOM, self.name + 'output' )
        self.enInputV =  DataEntry(self.frData, self.name+"inputV", True, 6 )
        self.enInputI =  DataEntry(self.frData, self.name+"inputI", True, 6 )
        self.enSetpoint = DataEntry(self.frData, self.name+'setpoint', False, 15 )
        self.enData1 = DataEntry(self.frData, self.name+'data', False, 7 )
        self.enData2 = DataEntry(self.frData, self.name+'data', False, 7 )
        
        # if self.name == "Heat 2":
        #     self.vFollow = tk.IntVar()
        #     self.chFollow = ttk.Checkbutton(self.frData, text='Follow Heat 1', variable = self.vFollow, onvalue = 1, offvalue = 0 ) #, 
# 	    command=metricChanged, variable=measureSystem,
# 	    onvalue='metric', offvalue='imperial')
        self.initLabels()
        self.initLocations()

        
    def initLabels(self):
        super().initLabels()
        # self.lblFilamentNumber = ttk.Label( self.frData, text = '(Filaments)', style = 'Std.TLabel' )
        # self.lblTitle = ttk.Label(self, text = self.name, style = 'Header.TLabel' )
        # self.lblCOMStatus = ttk.Label( self.frCOM, text = 'COM Status', style = 'Std.TLabel' )
        # self.lblOutput = ttk.Label( self.frCOM, text = 'Output', style = 'Std.TLabel' )
        
        # self.lblRampTime = ttk.Label(self.frData, text = 'Ramp Time:', style = 'Std.TLabel' )
        # self.lblSetpoint = ttk.Label(self.frData, text = 'Setpoint:', style = 'Std.TLabel' )
        
        self.lblInputV = ttk.Label( self.frData, text = 'Input Set V:', style = 'Std.TLabel' )
        self.lblUnitV = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
        self.lblInputI = ttk.Label( self.frData, text = 'Input Set I:', style = 'Std.TLabel' )
        self.lblUnitA = ttk.Label( self.frData, text = 'A', style = 'Std.TLabel' )
        # self.lblUnit2 = ttk.Label( self.frData, text = 'V,A', style = 'Std.TLabel' )
        
    
    def updateWidgets(self, ports, portStatus, outputStatus, setpoints, dataV, dataI, autoMode ):
        # print("updateWidgets() method called from fr" + self.name)
        self.btConnect.updateStatus( portStatus )
        self.ltCOM.updateStatus( portStatus )
        self.listCOM.updateStatus( portStatus, ports )
        if portStatus == 1:
            self.btOutput.updateStatus( outputStatus )
            self.btSetInput.updateStatus( 1 )
            self.ltActive.updateStatus( outputStatus )
            self.enSetpoint.setData( '{:.1f} V, {:.2f} A'.format(setpoints[0], setpoints[1]) )
            self.listRamp.unlock()
            self.enData1.setData( '{:.3f} V   {:.3f} A'.format(dataV, dataI) )
            #if dataT > 1500:
            #    self.enData2.setData( '{:.1f} W   {:.0f} K'.format(dataQ, dataT ) )
            #else:
                # Assumptions are probably not valid for temperatures under 1500K
            #    self.enData2.setData( '{:.1f} W   ---- K'.format(dataQ) )
        else:
            self.btOutput.updateStatus( 0 )
            self.btSetInput.updateStatus( 0 )
            self.ltActive.updateStatus( 0 )
            self.enSetpoint.setData( 'n/a' )
            self.listRamp.lock()
            self.enData1.setData( '-.--- V   -.--- A' )
            #self.enData2.setData( '---.- W   ---- K' )
            
        if autoMode == 1:
            self.btOutput.updateStatus( 0 )
            self.btSetInput.updateStatus( 0 )
    
    
    def initLocations(self):
        print("initializing widgets & placement for ", self.name )
        self.columnconfigure( index=0, weight=0 )
        self.rowconfigure( index=0, weight=0 )
        self.rowconfigure( index=1, weight=1)
        self.rowconfigure( index=2, weight=2)
        
        # self['width'] = '5c'
        self['padding'] = ('0.1c', '0.1c')
        
        self.lblTitle.grid( row = 0, column = 0 )
        
        self.frCOM.columnconfigure(index=0, weight=0)
        self.frCOM.rowconfigure(index=0, weight=1)
        # self.frCOM['relief'] = 'raised'
        self.frCOM['padding'] = ('0.1c', '0.25c')
        self.frCOM.grid( row = 1, column = 0, sticky = ' nsew' )  #Not the problem
        self.listCOM.grid( row = 0, column = 1 )
        self.btConnect.grid( row = 0, column = 3, padx = 10 )
        self.ltCOM.grid( row = 1, column = 0, sticky = 'w' )
        self.lblCOMStatus.grid( row = 1, column = 1)
        self.lblOutput.grid( row = 1, column = 3, sticky = 'e')
        self.ltActive.grid( row = 1, column = 4)
        
        
        self.frData.columnconfigure(index=0, weight=0)
        self.frData.rowconfigure(index=0, weight=1)
        self.frData.rowconfigure(index=1, weight=1)
        self.frData.rowconfigure(index=2, weight=2)
        # self.frData['relief'] = 'sunken'
        self.frData['padding'] = ('0.1c', '0.1c')
        self.frData.grid( row = 2, column = 0, sticky = ' nsew' )
        self.lblRampTime.grid( row = 0, column = 0 )
        self.listRamp.grid( row = 0, column = 2 )
        self.lblInputI.grid(row = 1, column = 0, columnspan = 1 )
        self.lblInputV.grid(row = 2, column = 0, columnspan = 1)
        self.enInputV.grid( row = 1, column = 2)
        self.enInputI.grid( row = 2, column = 2)
        self.lblUnitA.grid( row = 1, column = 3, sticky = 'w')
        self.btSetInput.grid(row = 1, column = 4, rowspan = 2, sticky='ns')
        
        
        self.lblSetpoint.grid( row = 3, column = 0 )
        self.enSetpoint.grid( row = 3, column = 2, columnspan = 3, sticky = 'w')
        # self.lblUnit2.grid( row = 3, column = 3, sticky = 'w' )
        self.lblUnitV.grid( row = 2, column = 3, sticky = 'w' )
        # if self.name == "Heat 2":
        #     self.chFollow.grid( row = 2, column = 4 )
        # self.lblFilamentNumber.grid( row = 3, column = 4)
        
        self.enData1.grid( row = 4, column = 0, rowspan = 2, columnspan = 3, sticky = 'nsew')
        #self.enData2.grid( row = 4, column = 0, rowspan = 2, columnspan = 3, sticky = 'nsew')
        self.btOutput.grid( row = 5, column = 4)
        
    # def setFilamnetNumber(self, numberFilaments):
    #     self.lblFilamentNumber['text'] = ("({:d} Filaments)".format(numberFilaments))
    #     self.numFilaments = numberFilaments
        