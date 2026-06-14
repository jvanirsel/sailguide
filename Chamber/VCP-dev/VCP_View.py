import tkinter as tk
from tkinter import font
from tkinter import ttk as ttk
from VCP_GUI_Elements import *
from MotorControllerFrame import MotorControllerFrame
from PressureControlSystemFrame import PressureControllerFrame
from BKPrecisionFrame import BKP9115Frame
from PlasmaSourceFrame import PlasmaSourceFrame
from WSLPFrame import WSLPFrame
from PlotFrame import PlotFrame
from AutomaterFrame import AutomaterFrame
from PNIFrame import PNIFrame
from RPAFrame import RPAFrame
import serial.tools.list_ports


class View( ttk.Frame ):
    def __init__(self, root):
        super().__init__( root )
        self.root = root
        
        self.names = [ 'mc', 'l392', 'pcs', 'heat1', 'heat2', 'bias', 'wslp' ]
        self.flgUpdate = False
        self.flgAuto = False
        self.flgCOM = { 'mc':-1, 'l392':-1, 'pcs':-1, 'heat1':-1,'heat2':-1, 'bias':-1, 'wslp':-1 }
        self.flgActive = { 'mc':0, 'l392':0, 'pcs':-1, 'heat1':1,'heat2':1, 'bias':1, 'wslp':0 }
        
        self.autoMode = -1
        self.repeatMode = -1
        self.dvAutoProgress = tk.IntVar()
        
        # # MC nodes
        self.dvMotorPosition = { 'z': 45.2, 't':16.6 } # [Zpos,Tpos]
        
        # # Lesker/PCS nodes
        self.dvPressure = 0.0
        self.dvPressurePlot = 0.0
        self.dvPCSSetpoint = 0.0
        
        # # BKP nodes
        self.dvSourceV = { 'heat1':0.0, 'heat2':0.0, 'bias':0.0 }
        self.dvSourceI = { 'heat1':0.0, 'heat2':0.0, 'bias':0.0 }
        self.dvSourceW = { 'heat1':0.0, 'heat2':0.0 }
        self.dvSourceTemp = { 'heat1':0.0, 'heat2':0.0 }
        self.dvSourceSetV = { 'heat1':0.0, 'heat2':0.0, 'bias':0.0 }
        self.dvBiasCurrentPlot = []
        self.dvBiasVoltagePlot = []
        self.dvSourceTempPlot = []
        
        # # WSLP Nodes
        self.dvCh1 = []
        self.dvCh2 = []
        self.dvH = {}
        
        # # PNI Nodes IH change
        self.dvMagField = {}

        # # RPA Nodes
        self.RPAData = {}
        self.RPASupportData = {}
        
        
        self.createStyles()
        self.frames = {}
        self._add_Frame( PlasmaSourceFrame, 'frSources')
        self._add_Frame( PressureControllerFrame, 'frPC' )
        self._add_Frame( MotorControllerFrame, 'mc' )
        self._add_Frame( PlotFrame, 'frPlot' )
        self._add_Frame( WSLPFrame, 'wslp' )
        self._add_Frame( PNIFrame, 'pni')
        self._add_Frame( RPAFrame, 'rpa')
        # for future reference, grabbing a reference to the important subframes
        # NOT including plots, automater
        self.frames.update( {'l392':self.frames['frPC'].frL392, 'pcs':self.frames['frPC'].frPCS,\
                'heat1':self.frames['frSources'].frHeat1, 'heat2':self.frames['frSources'].frHeat2,\
                'bias':self.frames['frSources'].frBias} )
        try:
            self.gridFrames()
        except:
            print("goof on setting up grid frame. Yikes.")

        # Misc
        self.availablePorts = ''
        self.plotVal = 'pressure'
        print("view finished initiatizing")
        self.badCounter = 0
        # self.counter = 0 # for debugging
        
        # Preset com ports
        ports = [port.name for port in serial.tools.list_ports.comports()]
        if 'COM5' in ports:
            self.frames['heat1'].listCOM.set('COM5')
        if 'COM4' in ports:
            self.frames['heat2'].listCOM.set('COM4')
        if 'COM6' in ports:
            self.frames['bias'].listCOM.set('COM6')
        if 'COM10' in ports:
            self.frames['mc'].listCOM.set('COM10')
        if 'COM8' in ports:
            self.frames['pcs'].listCOM.set('COM8')
        if 'COM3' in ports:
            self.frames['l392'].listCOM.set('COM3')
        if 'COM9' in ports:
            self.frames['wslp'].listCOM.set('COM9')
        if 'COM23' in ports:
            self.frames['wslp'].listCOM.set('COM23')
        if 'COM22' in ports:
            self.frames['wslp'].listCOM.set('COM22')
        
    def updateDisplay(self):
        # print("updateDisplay() method called from View object")
        if self.flgUpdate == True:
            
            self.frames['mc'].updateWidgets( self.availablePorts, self.flgCOM['mc'],\
                        self.flgActive['mc'], self.dvMotorPosition['z'], self.dvMotorPosition['t'], \
                            self.autoMode, self.repeatMode )
                

            self.frames['frPC'].updateWidgets( self.availablePorts, self.flgCOM['l392'],\
                        self.flgCOM['pcs'],  self.flgActive['l392'], self.flgActive['pcs'],\
                        self.dvPressure, self.dvPCSSetpoint, self.dvPressurePlot, \
                        self.dvBiasVoltagePlot, self.dvBiasCurrentPlot, self.dvSourceTempPlot, self.plotVal, self.autoMode )
            
                
            self.frames['frSources'].updateWidgets( self.availablePorts,\
                        [self.flgCOM['heat1'], self.flgCOM['heat2'], self.flgCOM['bias']],\
                        [self.flgActive['heat1'], self.flgActive['heat2'], self.flgActive['bias']],\
                        self.dvSourceSetV, self.dvSourceV, self.dvSourceI, self.dvSourceW, self.dvSourceTemp, self.autoMode )

            self.frames['wslp'].updateWidgets( self.availablePorts, self.flgCOM['wslp'], self.flgActive['wslp'], self.dvH, self.autoMode )
            
            # self.frames['pni'].updateWidgets( self.autoMode )
            
            self.frames['frPlot'].updateWidgets( self.dvCh1, self.dvCh2, self.dvH['boardID'], self.autoMode, self.flgCOM['wslp'] )
            
            self.frames['pni'].updateWidgets( self.availablePorts, self.flgCOM['pni'], self.flgActive['pni'], \
                                              self.autoMode, self.dvMagField ) # IH change
            
            self.frames['rpa'].updateWidgets (self.availablePorts, self.flgCOM['rpa'], self.flgActive['rpa'], \
                                              self.RPAData, self.RPASupportData)
            
            # if self.autoMode == 1:
        
            self.flgUpdate = False
            self.badCounter = 0
            self.root.after( 500, self.updateDisplay ) 
        else:
            # print("Update triggered, but no new data available")
            self.badCounter = self.badCounter + 1
            if(self.badCounter > 20):
                print("No data available for 2 seconds. Help please. Ending method without recursion...")
                return
            # this needs to be filled out more.
            self.root.after( 100, self.updateDisplay ) 
            
            
    def gridFrames(self):
        print("adding farmes to parent grid")
        self.frames['frSources'].grid( row = 0, column = 0, rowspan = 3,  sticky = 'nsew' )
        self.frames['frPlot'].grid( row = 0, column = 2, columnspan = 2, rowspan = 2, sticky = 'nsew')
        self.frames['mc'].grid( row = 2, column = 3, columnspan = 2, sticky = 'nsew' )
        self.frames['frPC'].grid( row = 2, column = 1, columnspan = 2, sticky = 'nsew' )
        self.frames['wslp'].grid( row = 0, column = 1, rowspan = 2, sticky= 'nesw' )
        self.frames['pni'].grid( row = 0, column = 4, sticky = 'nesw' )
        self.frames['rpa'].grid( row = 1, column = 4, sticky = 'nsew') 
        #     ______0_______1____2____3_____4____
        #  0  | (Source, |_WSLP_|___Plot__|_PNI_|
        #  1  |  Source) |     PCS   | MC(Scan) |
        
        
    def createSubFrames(self): # create the frames that need nodes passed into them.
        print("createSubFrames() method called from View object")
        self.frMotorController = MotorControllerFrame( self, self.listPorts[0], self.btConnect[0], self.btActive[0],\
            self.btMotorStop, self.ltCOM[0], self.ltActive[0], self.enMotorControl[0], self.enMotorControl[1] )
            
        self.frPressureController =  PressureControllerFrame( self, self.listPorts[1], self.listPorts[2],\
            self.btConnect[1], self.btConnect[2], self.btActive[1], self.btActive[2], self.btPCSSet,\
            self.ltCOM[1], self.ltCOM[2], self.ltActive[1], self.ltActive[2], self.enPCS )
            
        self.frPlasmaSource = PlasmaSourceFrame( self, self.listPorts[3:6], self.btConnect[3:6], self.btActive[3:6],\
            self.btBKPSetInput, self.ltCOM[3:6], self.ltActive[3:6], self.enBKPInput )
            
        self.frWSLP = WSLPFrame(self)
        

    def _add_Frame(self, Frame, name, args=None):
        if args is None:
            self.frames[name] = Frame(self.root)
        else: 
            self.frames[name] = Frame(self.root, args)
        self.frames[name].initWidgets()
        

    def createStyles(self):
        print("createStyles() method called from View")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        # print( self.style.lookup('TButton', 'padding') )
        # self.style.configure( 'Std.TButton', font=('Helvetica', 14), padding=(2) )
        self.style.configure( 'Raised.TButton', relief = 'raised', font=('Helvetica', 14) , padding=(0,0,0,0), justify = 'center' ) #[('!pressed', 'sunken'), ('pressed', 'raised')] )
        self.style.configure( 'Sunken.TButton', relief = 'sunken', font=('Helvetica', 14), padding=(0,0,0,0), justify = 'center' ) 
        self.style.configure( 'Neutral.TButton', relief = 'flat', font=('Helvetica', 14), padding=(0,0,0,0), justify = 'center' )
        
        # self['justify'] = 'center'
        
        self.style.configure( 'Header.TLabel', font = ('Helvetica', 24) )
        self.style.configure( 'Med.TLabel', font = ('Helvetica', 18) )
        self.style.configure( 'Std.TLabel', font = ('Helvetica', 14) )
        # self.style.configure( )
        
        self.style.configure( 'Light.TButton', relief = 'flat', padding = (0,0,0,0))
        
        self.style.configure( 'Std.TRadiobutton', font = ('Helvetica', 14) )
        self.style.configure( 'Std.TCheckbutton', font = ('Helvetica', 14) )
        
        bigfont = font.Font(family="Helvetica",size=14)
        self.root.option_add("*TCombobox*Listbox*Font", bigfont)
        self.root.option_add("*TCombobox*Font", bigfont)
        

        self.style.configure("bar.Horizontal.TProgressbar", background='green') #lightcolor='green', darkcolor='blue',

        
    
    # Below are Depreciated. From Early Development
        ''' 
        ## From init
        # # attrs include all control nodes (bt.s, listBoxes, etc).     Lights?
        # #               also all status flags & data vars
        # #               All common nodes&flags will be in arrays. Uniques (filament status, etc.) will be 
        # # Array index:    0: Motor Controller
        #                 # 1: Lesker 392
        #                 # 2: PCS
        #                 # 3,4,5: Heat 1, Heat 2, Bias
        #                 # 6: WSLP
        
        
    def createControlNodes( self ):
        print("createControlNodes() method called from View object")
        
        print("\n!\n!\n!\nHELLO\n!\n!\n!\n")
        for i  in range(7):
            self.btConnect[i] = ConnectButton( self, self.names[i] + 'connct' )
            self.btActive[i] = PushButton( self, self.names[i] + 'active')
            self.listPorts[i] = PortSelectorBox( self, self.names[i] )
            self.ltCOM[i] = StatusLight( self, self.names[i] + 'com' )
            self.ltActive[i] = StatusLight( self, self.names[i] + 'output')
        
        self.btActive[0] = ClickButton( self, self.names[0]+'move') # for motor move button. Overwrites previous
        self.btMotorStop = ClickButton( self, self.names[0]+'stop' )
        self.btPCSSet =  ClickButton( self, self.names[2]+'set')
        self.btBKPSetInput = [  ClickButton( self, self.names[3]+'set' ),\
                                ClickButton( self, self.names[4]+'set' ),\
                                ClickButton( self, self.names[5]+'set' ) ]
        
        self.enMotorControl = [ DataEntry(self, self.names[0]+"inputZ", True ),\
                                DataEntry(self, self.names[0]+"inputT", True ) ]
            
        self.enBKPInput = [ DataEntry(self, self.names[3]+"inputV", True),\
                            DataEntry(self, self.names[4]+"inputV", True),\
                            DataEntry(self, self.names[5]+"inputV", True) ]
            
        self.btWSLPSweeps = [ ClickButton( self, self.names[6]+'genProfile' ),\
                              ClickButton( self, self.names[6]+'programSweep' ),\
                              ClickButton( self, self.names[6]+'saveDir' ) ]
        self.btWSLPCancel =   ClickButton( self, self.names[6]+'cancel' )
        # self. # Finish WSLP control nodes here please
        
        
    def packFrames(self):
        # self.frMotorController.pack()
        # self.frMotorController.initLocations()
        # self.frPressureController.pack()
        # self.frPressureController.initLocations()
        self.frPlasmaSource.pack()
        self.frPlasmaSource.initLocations()
        # self.frWSLP.pack()
            
    def initControlNodes(self):
        print("initControlNodes() method called from View object")
        # maybe
        
        
    def bindControlNodes(self):
        print("bindControlNodes() method called from View class")
        self.controller.bindControlNodes( self.btConnect )
        
    def setController(self, controller):
        print("setController() method called from View class")
        self.controller = controller
    

    def updateStatuses(self):
        pass
    
    def setflgCOM(self, flag):
        self.flgCOM[0:7] = flag
        
    def chagneZ(self):
        # print('y')
        z = self.dvMotorPosition['z']  + 10
        # print("changing position to ", z)
        self.dvMotorPosition['z'] = z
        self.dvMotorPosition['t'] = self.dvMotorPosition['t']+6
        '''


# Create MotorController Frame - TEST
# self.btConnect[0] = ConnectButton(self, 'name 1')
# print("View's button name (before init) is  ", self.btConnect[0].name)
# self.frMC = MotorControllerFrame( self, self.lstPortSelector[0], self.btConnect[0], self.btActive[0], self.btMotorStop, self.ltCOM[0], self.ltActive[0], self.dvMotorControl[0], self.dvMotorControl[1], self.dvMotorControl[2], self.dvMotorControl[3] )

# self.frMC.testInitBtConnect() # will not be called here
# self.frMC.pack() # will not be called here
# print("frMC's button name (after init) is  ", self.frMC.btConnect.name)
# print("View's button name (after init) is  ", self.btConnect[0].name)