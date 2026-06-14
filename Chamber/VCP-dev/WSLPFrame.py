import tkinter as tk
import tkinter.ttk as ttk
from VCP_GUI_Elements import *


class WSLPFrame( ttk.Frame ):
    def __init__(self, parent):
        super().__init__(parent)
        self['borderwidth'] = 1
        self['relief'] = 'solid'
        
    def updateWidgets(self, ports, portStatus, outputStatus, header, autoMode ):
        self.btConnect.updateStatus( portStatus )
        self.ltCOM.updateStatus( portStatus )
        self.listCOM.updateStatus( portStatus, ports )
        self.btProgramSweep.updateStatus( portStatus )
        if portStatus == 1:
            self.btOutput.updateStatus( 1 )
            self.btCancel.updateStatus( 1 )
            self.ltActive.updateStatus( outputStatus )
        else:
            self.btOutput.updateStatus( 0 )
            self.btCancel.updateStatus( 0 )
        
        if autoMode == 1:
            self.btOutput.updateStatus( 0 )
            self.btCancel.updateStatus( 0 )
            self.btProgramSweep.updateStatus( 0 )
            self.chSaveMe.state(['disabled', 'selected']) 
        else:
            self.chSaveMe.state(['!disabled'])  
            
    def updateParameters(self, header):
        # if header['boardID'] == 2:
        try:
            # print(" Update Parameters Called!")
            # self.lblNumDwells.configure( text = "# Groups:")
            self.enNumSteps.setData( str(header['numSteps']) )
            self.enNumSweeps.setData( str(header['numSweeps']) )
            self.enNumDwells.setData( str(header['numDwells']) )
            self.enNumSamples.setData( str(header['numSamples']) )
            self.enNumGroups.setData( str(header['numGroups']) )
            # self.listDwellSide.setSelection()
            self.enEstFreq.setData( "{:.1f}Hz".format(header['estFreq']) )
        except:
            print("Error updating parameters")
            
        # elif header['boardID'] == 1:
        #     print("No parameters to update for v2.1 board")
            # self.lblNumDwells.configure( text = '# Dwell pts:')
            
        
    
    def initWidgets(self):
        print("initWidgets() method called for WSLPFrame")
        self.frCOM = ttk.Frame(self)
        self.frParams = ttk.Frame(self)
        
        self.listCOM = PortSelectorBox( self.frCOM, 'WSLP' )
        self.btConnect = ConnectButton( self.frCOM, 'WSLPconnect' )
        self.ltCOM = StatusLight( self.frCOM, 'WSLPcom' )
        self.ltActive = StatusLight( self.frCOM, 'WSLPoutput' )
        self.btOutput =  ClickButton( self, 'WSLPactive')
        self.btCancel = ClickButton( self, 'WSLPstop')
        self.btGenProfile =  ClickButton( self, 'WSLPgenProfile')
        self.btProgramSweep =  ClickButton( self, 'WSLPprogramSweep')
        self.btSetDir =  ClickButton( self, 'WSLPsetDir')
        self.btUpdateFilename = ClickButton( self, 'WSLPUpdateFilename' )
        
        self.dwellVar = tk.StringVar()
        # self.rbtIonDwell = ttk.Radiobutton( self.frParams, text = 'Ion Dwell', variable = self.dwellVar, value = 'ion', style='Std.TRadiobutton' )
        # self.rbtEDwell = ttk.Radiobutton( self.frParams, text = 'e Dwell', variable = self.dwellVar, value = 'electron', style='Std.TRadiobutton' )
        self.dwellVar.set('ion')
        
        self.enNumSteps = DataEntry( self.frParams, "WSLPNumSteps", True, 5 )
        self.enNumSweeps = DataEntry( self.frParams, "WSLPNumSweeps", True, 5 )
        self.enNumGroups = DataEntry( self.frParams, "WSLPNumGroups", True, 5)
        self.enNumDwells = DataEntry( self.frParams, "WSLPNumDwell", True, 5 )
        self.enNumSamples = DataEntry( self.frParams, "WSLPNumSamples", True, 5 )
        self.enNumSteps.setData('1000')
        self.enNumSweeps.setData('4')
        self.enNumDwells.setData('2')
        self.enNumSamples.setData('1')
        self.enNumGroups.setData('3')
        
        self.enEstFreq = DataEntry( self.frParams, "WSLPSwpFreq", False, 7 )
        
        self.listDwellSide = SelectorBox(self.frParams, 'DwellSideSelector')
        self.listDwellSide.setList( ['ion', 'electron', 'alt'] )
        self.listDwellSide.setSelection('ion')
        
        
        self.enDataPrefix = DataEntry( self.frParams, "WSLPPrefix", True, 10 )
        self.enDataSuffix = DataEntry( self.frParams, "WSLPSuffix", True, 10 )
        self.enFileName = DataEntry(self.frParams, "WSLPFileName", False, 20 )
        self.enFileName.setData('n/a')
        
        self.vSaveMe = tk.IntVar()
        self.chSaveMe = ttk.Checkbutton(self, text='Save?', variable = self.vSaveMe, onvalue = 1, offvalue = 0 )
        self.chSaveMe['style']  = 'Std.TCheckbutton'
        
        self.initLabels()
        self.initLocations()

        
        
    def initLabels(self):
        self.lblTitle = ttk.Label(self, text = 'WSLP', style = 'Header.TLabel' )
        self.lblCOMPort = ttk.Label( self.frCOM, text = 'COM Port:', style = 'Std.TLabel' )
        self.lblCOMStatus = ttk.Label( self.frCOM, text = 'COM Status', style = 'Std.TLabel' )
        self.lblOutput = ttk.Label( self.frCOM, text = 'Sweeping', style = 'Std.TLabel' )
        
        self.lblSweepParams = ttk.Label( self.frParams, text = 'Sweep Parameters:', style = 'Std.TLabel' )
        self.lblNumSteps = ttk.Label( self.frParams, text = '# Steps/Leg:', style = 'Std.TLabel' )
        self.lblNumSweeps = ttk.Label( self.frParams, text = '# Sweeps/Group:', style = 'Std.TLabel' )
        self.lblNumDwells = ttk.Label( self.frParams, text = '# Dwell Segments:', style = 'Std.TLabel' )
        self.lblNumGroups = ttk.Label( self.frParams, text = '# Sweep Groups:', style = 'Std.TLabel')
        self.lblNumSamples = ttk.Label( self.frParams, text = '# Samples/Step:', style = 'Std.TLabel' )
        self.lblDwellSide = ttk.Label( self.frParams, text = 'Dwell Side:', style = 'Std.TLabel')
        # self.lblUnit1 = ttk.Label( self.frParams, text = '', style = 'Std.TLabel' )
        
        self.lblDataPrefix = ttk.Label( self.frParams, text = 'Sensor Info: ', style = 'Std.TLabel' )
        self.lblDataSuffix = ttk.Label( self.frParams, text = 'Conditions: ', style = 'Std.TLabel' )
        
        self.lblFileName = ttk.Label( self.frParams, text = 'Filename is:', style = 'Std.TLabel' )
        
        self.lblEstFreq = ttk.Label( self.frParams, text = 'Est. Frequency: ', style = 'Std.TLabel')
        
        # self.lblSetpoint = ttk.Label(self.frData, text = 'Setpoint:', style = 'Std.TLabel' )
        # self.lblInput = ttk.Label( self.frData, text = 'Input Set V:', style = 'Std.TLabel' )
        # self.lblUnit1 = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
        # self.lblUnit2 = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
    
    def initLocations(self):
        print("initializing widgets & placement for WSLP frame" )
        self.columnconfigure( index=0, weight=0 )
        # self.columnconfigure( index=1, weight=0 )
        # self.columnconfigure( index=2, weight=0 )
        self.rowconfigure( index=0, weight=0 )
        self.rowconfigure( index=1, weight=1)
        self.rowconfigure( index=2, weight=1)
        self.rowconfigure( index=3, weight=1)
        self.rowconfigure( index=4, weight=1)
        self.rowconfigure( index=5, weight=1)
        self.rowconfigure( index=6, weight=5)
        self['padding'] = ('0.1c', '0.1c')
        
        self.lblTitle.grid( row = 0, column = 0, columnspan = 2 )
        
        self.frCOM.columnconfigure(index=2, weight=1)
        # self.frCOM.rowconfigure(index=0, weight=1)
        self.frCOM['padding'] = ('0.1c', '0.25c')
        # self.frCOM['relief'] = 'sunken'
        self.frCOM.grid( row = 1, column = 0, columnspan = 2, sticky = ' ew' )
        self.lblCOMPort.grid( row = 0, column = 1)
        self.listCOM.grid( row = 0, column = 2 )
        self.btConnect.grid( row = 0, column = 3)#, padx = 10 )
        self.ltCOM.grid( row = 1, column = 0 )
        self.lblCOMStatus.grid( row = 1, column = 1)
        self.lblOutput.grid( row = 1, column = 3)
        self.ltActive.grid( row = 1, column = 4)
        
        
        self.frParams.columnconfigure(index=0, weight=1)
        self.frParams.columnconfigure(index=1, weight=1)
        self.frParams.columnconfigure(index=2, weight=0)
        self.frParams.rowconfigure(index=0, weight=1)
        self.frParams.rowconfigure(index=5, weight=1)
        self.frParams.rowconfigure(index=9, weight=1)
        # self.frParams.rowconfigure(index=2, weight=1)
        # self.frParams.rowconfigure(index=3, weight=1)
        # self.frParams.columnconfigure(index=0, weight=0)
        self.frParams['relief'] = 'sunken'
        self.frParams['padding'] = ('0.1c', '0.1c')
        self.frParams.grid( row = 2, column = 0, sticky = ' nsew', rowspan = 6 )
        
        self.lblSweepParams.grid( row = 0, column = 0, columnspan=2, sticky = 'w')
        rowIndex = 1
        self.lblNumSamples.grid( row = rowIndex, column = 0 )
        self.enNumSamples.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        self.lblNumSteps.grid( row = rowIndex, column = 0 )
        self.enNumSteps.grid( row = rowIndex, column = 1 )
        # self.lblUnit1.grid( row = 1, column = 2, sticky = 'w' )
        rowIndex += 1
        self.lblNumSweeps.grid( row = rowIndex, column = 0 )
        self.enNumSweeps.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        self.lblNumDwells.grid( row = rowIndex, column = 0 )
        self.enNumDwells.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        self.lblNumGroups.grid( row = rowIndex, column = 0)
        self.enNumGroups.grid( row = rowIndex, column = 1)
        rowIndex += 1
        
        self.lblDwellSide.grid( row = rowIndex, column = 0 )
        self.listDwellSide.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        
        self.lblEstFreq.grid( row = rowIndex, column = 0 )
        self.enEstFreq.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        # self.rbtIonDwell.grid( row = 5, column = 0 )
        # self.rbtEDwell.grid( row = 5, column = 1 )
        
        self.lblDataPrefix.grid( row = rowIndex, column = 0, sticky = 'w' )
        self.lblDataSuffix.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        self.enDataPrefix.grid( row = rowIndex, column = 0, sticky='w' )
        self.enDataSuffix.grid( row = rowIndex, column = 1 )
        rowIndex += 1
        self.lblFileName.grid( row = rowIndex, column = 0, sticky = 'w' )
        self.enFileName.grid( row = rowIndex+1, column = 0, columnspan=2, sticky='ew' )
        rowIndex += 2
        
        self.btGenProfile.grid( row = 2, column = 1 )
        self.btProgramSweep.grid( row = 3, column = 1 )
        self.btSetDir.grid( row = 4, column = 1 )
        self.btUpdateFilename.grid( row = 5, column = 1)
        
        self.btOutput.grid( row = 6, column = 1 )
        # self.btCancel.grid( row = 6, column = 1)
        self.chSaveMe.grid( row = 7, column  = 1)