import tkinter as tk
import tkinter.ttk as ttk
from VCP_GUI_Elements import ClickButton, PushButton, ConnectButton, StatusLight, DataEntry, PortSelectorBox, RampTimeBox

class BKP9115Frame( ttk.Frame ):
    #Constructor
    def __init__(self, parent, name ): # listCOM, btConnect, btOutput, btSetInput, ltCOM, ltActive, enInput ):
        super().__init__(parent)
        self.name = name
        
        # self.geometry( "500x333" )
        # try:
        #     self.grid_propagate(0)
        #     self['width'] = 400
        #     self['height'] = round(1000/3)
        # except:
        #     print("don't like me")
        
        self['borderwidth'] = 1
        self['relief'] = 'solid'


        # self.initWidgets()

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
        self.enInput =  DataEntry(self.frData, self.name+"inputV", True, 6 )
        self.enSetpoint = DataEntry(self.frData, self.name+'setpoint', False, 6 )
        self.enData = DataEntry(self.frData, self.name+'data', False, 14 )
        # if self.name == "Heat 2":
        #     self.vFollow = tk.IntVar()
        #     self.chFollow = ttk.Checkbutton(self.frData, text='Follow Heat 1', variable = self.vFollow, onvalue = 1, offvalue = 0 ) #, 
# 	    command=metricChanged, variable=measureSystem,
# 	    onvalue='metric', offvalue='imperial')
        self.initLabels()
        self.initLocations()

        
    def initLabels(self):
        self.lblTitle = ttk.Label(self, text = self.name, style = 'Header.TLabel' )
        self.lblCOMStatus = ttk.Label( self.frCOM, text = 'COM Status', style = 'Std.TLabel' )
        self.lblOutput = ttk.Label( self.frCOM, text = 'Output', style = 'Std.TLabel' )
        
        self.lblRampTime = ttk.Label(self.frData, text = 'Ramp Time:', style = 'Std.TLabel' )
        self.lblSetpoint = ttk.Label(self.frData, text = 'Setpoint:', style = 'Std.TLabel' )
        self.lblInput = ttk.Label( self.frData, text = 'Input Set V:', style = 'Std.TLabel' )
        self.lblUnit1 = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
        self.lblUnit2 = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
        
    
    def updateWidgets(self, ports, portStatus, outputStatus, setpoint, dataV, dataI, autoMode ):
        # print("updateWidgets() method called from fr" + self.name)
        self.btConnect.updateStatus( portStatus )
        self.ltCOM.updateStatus( portStatus )
        self.listCOM.updateStatus( portStatus, ports )
        if portStatus == 1:
            self.btOutput.updateStatus( outputStatus )
            self.btSetInput.updateStatus( 1 )
            self.ltActive.updateStatus( outputStatus )
            self.enSetpoint.setData( setpoint )
            self.listRamp.unlock()
            self.enData.setData( '{:.3f} V   {:.3f} A'.format(dataV, dataI) )

            # if self.name == "Heat 2":
            #     self.chFollow.state(['enabled']) 
            #     if self.vFollow:
            #         print("wAHHoo")
            #     else:
            #         print("sads:(")
        else:
            self.btOutput.updateStatus( 0 )
            self.btSetInput.updateStatus( 0 )
            self.ltActive.updateStatus( 0 )
            self.enSetpoint.setData( 'n/a' )
            self.listRamp.lock()
            self.enData.setData( '-.--- V   -.--- A' )
            # if self.name == "Heat 2":
            #     self.chFollow.state(['disabled']) 
            
        if autoMode == 1:
            self.btOutput.updateStatus( 0 )
            self.btSetInput.updateStatus( 0 )
            
    
    def initLocations(self):
        print("initializing widgets & placement for ", self.name )
        self.columnconfigure( index=0, weight=0 )
        # self.columnconfigure( index=1, weight=0 )
        # self.columnconfigure( index=2, weight=0 )
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
        self.frData['padding'] = ('0.1c', '0.25c')
        self.frData.grid( row = 2, column = 0, sticky = ' nsew' )
        self.lblRampTime.grid( row = 0, column = 0 )
        self.listRamp.grid( row = 0, column = 2 )
        self.lblInput.grid(row = 1, column = 0, columnspan = 1 )
        self.enInput.grid( row = 1, column = 2)
        self.lblUnit1.grid( row = 1, column = 3, sticky = 'w')
        self.btSetInput.grid(row = 1, column = 4)
        
        
        self.lblSetpoint.grid( row = 2, column = 0) #, columnspan = 1 )
        self.enSetpoint.grid( row = 2, column = 2)
        self.lblUnit2.grid( row = 2, column = 3, sticky = 'w' )
        # if self.name == "Heat 2":
        #     self.chFollow.grid( row = 2, column = 4 )
        
        self.enData.grid( row = 3, column = 0, rowspan = 2, columnspan = 3, sticky = 'nsew')
        self.btOutput.grid( row = 3, column = 4)