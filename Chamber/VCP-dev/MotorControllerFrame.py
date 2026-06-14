import tkinter as tk
import tkinter.ttk as ttk
from VCP_GUI_Elements import *
from PIL import Image, ImageTk
from AutomaterFrame import AutomaterFrame
import numpy as np

class MotorControllerFrame( ttk.Frame ):
    #Constructor
    def __init__(self, parent, name = 'MC' ): #, listCOM, btConnect, btMove, btStop, ltCOM, ltActive, enInputZ, enInputT):
        super().__init__(parent)
        self.name ='frMC'
        
        # try:
        #     # self.
        #     # self.grid_propagate(0)
        #     # self['width'] = round((1800-400)/2)
        #     # self['height'] = round(1000/2)
        # except:
        #     print("don't like me")
        self.oldPositions= { 'z':200.0, 't':0.0 }
        self.dvAutoProgress = tk.IntVar()
        
        self.maxZScan = 160
        self.minZScan = 10
    
            
        self['borderwidth'] = 1
        self['relief'] = 'solid'
        self['padding'] = ('0.1c', '0.1c')
        
        
        # self.initWidgets()

    def initWidgets(self): # calls all subsequent methods
        self.frCOM = ttk.Frame( self )
        self.frData = ttk.Frame( self )
        self.frInputs = ttk.Frame( self )
        self.frInputs['borderwidth'] = 1
        self.frInputs['relief'] = 'solid'
        self.frPlot = ttk.Frame( self )
        self.frPlot['borderwidth'] = 1
        self.frPlot['relief'] = 'solid'
        self.listCOM = PortSelectorBox( self.frCOM, self.name )
        self.btConnect = ConnectButton( self.frCOM, self.name + 'connect' )
        self.btMove = ClickButton( self.frInputs, self.name + 'move' )
        self.btStop = ClickButton( self.frInputs, self.name + 'stop' )
        self.btCalibrate = ClickButton( self.frInputs, self.name+"calibrate" )
        self.ltCOM = StatusLight( self.frCOM, self.name + 'com' )
        self.ltActive = StatusLight( self.frCOM, self.name + 'move' )
        self.enInputZ = DataEntry( self.frInputs, self.name+'inZ', True, 6 )
        self.enInputT = DataEntry( self.frInputs, self.name+'inT', True, 6 )
        
        self.enPositionZ = DataEntry(self.frData, "MCposZ", False, 6)
        self.enPositionT = DataEntry(self.frData, "MCposT", False, 6)
        
        self.frAuto = ttk.Frame( self )
        self.frAuto['borderwidth'] = 1
        self.frAuto['relief'] = 'solid'
        self.btAuto = PushButton(self.frAuto, 'AutoStart')
        self.btRepeat = PushButton(self.frAuto, 'AutoRepeat')
        self.enStatus = DataEntry(self.frAuto, 'AutoStatus', editable=False, width=32)
        self.frAutoData = ttk.Frame( self.frAuto )
        self.enZFields = {}
        self.enZFields['Min'] = DataEntry(self.frAutoData, 'ZMin', editable=True, width=5)
        self.enZFields['Max'] = DataEntry(self.frAutoData, 'ZMax', editable=True, width=5)
        self.enZFields['Num'] = DataEntry(self.frAutoData, 'ZNum', editable=True, width=5)
        self.enZFields['Num'].setData('1')
        self.enTFields = {}
        self.enTFields['Min'] = DataEntry(self.frAutoData, 'TMin', editable=True, width=5)
        self.enTFields['Max'] = DataEntry(self.frAutoData, 'TMax', editable=True, width=5)
        self.enTFields['Num'] = DataEntry(self.frAutoData, 'TNum', editable=True, width=5)
        self.enTFields['Num'].setData('1')
        
        self.pbProgress = ttk.Progressbar( self.frAuto, orient=tk.HORIZONTAL, length = 100, mode='determinate', variable=self.dvAutoProgress, style="bar.Horizontal.TProgressbar")
        
        
        self.initLabels()
        self.initLocations()
     

    def initLabels(self):
        self.lblTitle = ttk.Label( self, text = 'Motor Controller', style = 'Header.TLabel' )
        self.lblCOMPort = ttk.Label( self.frCOM, text = 'COM Port:', style = 'Std.TLabel' )
        self.lblCOMStatus = ttk.Label( self.frCOM, text = 'COM Status', style = 'Std.TLabel' )
        self.lblMoving = ttk.Label( self.frCOM, text = 'Moving?', style = 'Std.TLabel' )
        self.lblZPosition  = ttk.Label( self.frData, text = 'Z Position:', style = 'Std.TLabel' )
        self.lblTPosition = ttk.Label( self.frData, text = 'T Position:', style = 'Std.TLabel' )
        self.lblUnit1 = ttk.Label( self.frData, text = 'cm', style = 'Std.TLabel' )
        self.lblUnit2 = ttk.Label( self.frData, text = 'deg', style = 'Std.TLabel' )
        self.lblMoveZ = ttk.Label( self.frInputs, text = 'Move Z to:', style = 'Std.TLabel' )
        self.lblMoveT = ttk.Label( self.frInputs, text = 'Move T to:', style = 'Std.TLabel' )
        self.lblUnit3 = ttk.Label( self.frInputs, text = 'cm', style = 'Std.TLabel' )
        self.lblUnit4 = ttk.Label( self.frInputs, text = 'deg', style = 'Std.TLabel' )
        
        self.lblAutoTitle = ttk.Label(self.frAuto, text = 'Motor Scan', style = 'Med.TLabel' )
        self.lblZRange = ttk.Label(self.frAutoData, text='Distance:', style = 'Std.TLabel')
        self.lblTRange = ttk.Label(self.frAutoData, text = "Angle:", style = 'Std.TLabel')
        self.lblMin = ttk.Label(self.frAutoData, text = 'Start', style = 'Std.TLabel' )
        self.lblMax = ttk.Label(self.frAutoData, text = 'Stop', style = 'Std.TLabel' )
        self.lblNum = ttk.Label(self.frAutoData, text = '# Points', style = 'Std.TLabel' )
        self.lblStatus = ttk.Label(self.frAuto, text='Status:', style = 'Std.TLabel')
        

    def initLocations(self):
        self.columnconfigure( index=0, weight=1 )
        self.columnconfigure( index=1, weight=1 )
        self.columnconfigure( index=2, weight=1 )
        self.rowconfigure( index=0, weight=1 )
        self.rowconfigure( index=1, weight=2 )
        self.rowconfigure( index=2, weight=2 )
        # self.rowconfigure( index=3, weight=20 )
        
        
        self.lblTitle.grid( row = 0, column = 0, columnspan=3)#, sticky = ' nsew' )
        
        self.frCOM.columnconfigure( index=3, weight=1 )
        self.frCOM.rowconfigure( index=0, weight=0 )
        self.frCOM['padding'] = ('0.5c', '0.15c')
        # self.frCOM['relief'] = 'raised'
        self.frCOM.grid( row = 1, column = 0, columnspan = 2, sticky = ' nsew' )
        self.lblCOMPort.grid( row = 0, column = 1 )
        self.listCOM.grid( row = 0, column = 2 )
        self.btConnect.grid( row = 0, column = 3 )
        self.lblCOMStatus.grid( row = 1, column = 1 )
        self.ltCOM.grid( row = 1, column = 0 )
        self.lblMoving.grid( row = 2, column = 1 )
        self.ltActive.grid( row = 2, column = 0 )
        
        self.frAuto.grid(row = 1, column = 2, rowspan = 3, sticky = 'nesw')
        self.frAuto['padding'] = ('0.1c', '0.1c')
        self.frAuto.rowconfigure( index=0, weight=1 )
        self.frAuto.rowconfigure( index=1, weight=2 )
        self.frAuto.rowconfigure( index=2, weight=1 )
        self.frAuto.rowconfigure( index=3, weight=1 )
        self.lblAutoTitle.grid(row = 0, column = 0, columnspan = 4)
        self.frAutoData.grid(row = 1, column = 0, columnspan = 4, sticky='nesw')
        self.frAutoData.rowconfigure( index=0, weight=0 )
        self.frAutoData.rowconfigure( index=1, weight=1 )
        self.frAutoData.rowconfigure( index=2, weight=1 )
        self.lblMin.grid(row = 1, column = 1)
        self.lblMax.grid(row = 1, column = 2)
        self.lblNum.grid(row = 1, column = 3)
        self.lblZRange.grid(row = 2, column = 0, sticky = 'e')
        pad = 7
        self.enZFields['Min'].grid( row = 2, column = 1, padx = pad )
        self.enZFields['Max'].grid( row = 2, column = 2, padx = pad )
        self.enZFields['Num'].grid( row = 2, column = 3, padx = pad )
        
        self.lblTRange.grid( row = 3, column = 0, sticky = 'e')
        self.enTFields['Min'].grid( row = 3, column = 1 )
        self.enTFields['Max'].grid( row = 3, column = 2 )
        self.enTFields['Num'].grid( row = 3, column = 3 )
        self.lblStatus.grid(row = 4, column = 0)
        self.enStatus.grid(row = 5, column = 0, columnspan = 4)
        self.pbProgress.grid(row = 6, column = 0, columnspan=4, sticky='ew')
        self.btAuto.grid(row = 7, column = 0, columnspan = 2, sticky='ew')
        self.btRepeat.grid(row = 7, column = 2, columnspan = 2, sticky='ew')
        
        
        
        self.frData.columnconfigure( index=0, weight=1 )
        self.frData.rowconfigure( index=0, weight=1 )
        self.frData['padding'] = ('0.5c', '0.1c')
        self.frData.grid( row = 2, column = 0, columnspan=2, sticky = ' nsew')
        self.lblZPosition.grid( row = 0, column = 0 )
        self.enPositionZ.grid( row = 0, column = 1 )
        self.lblUnit3.grid( row = 0, column = 2 )
        self.lblTPosition.grid( row = 1, column = 0 )
        self.enPositionT.grid( row = 1, column = 1 )
        self.lblUnit4.grid( row = 1, column = 2 )
        
        self.frInputs.columnconfigure( index=0, weight=1 )
        self.frInputs.columnconfigure( index=1, weight=1 )
        self.frInputs.columnconfigure( index=2, weight=0 )
        self.frInputs.rowconfigure( index=0, weight=1 )
        self.frInputs['padding'] = ('0.5c', '0.15c')
        self.frInputs.grid( row = 3, column = 0, columnspan=2, sticky = 'nsew' )
        self.lblMoveZ.grid( row = 0, column = 0 )
        self.enInputZ.grid( row = 0, column = 1 )
        self.lblUnit1.grid( row = 0, column = 2, sticky = 'w' )
        self.lblMoveT.grid( row = 1, column = 0 )
        self.enInputT.grid( row = 1, column = 1 )
        self.lblUnit2.grid( row = 1, column = 2, sticky = 'w' )
        self.btMove.grid( row = 2, column = 0 )
        self.btStop.grid( row = 2, column = 1, padx=10 )
        self.btCalibrate.grid( row = 2, column = 2 )

        
        self.frPlot.grid( row = 4, column = 0, columnspan = 3, sticky = ' nsew' )
        self.initPlotFrame()
        
    def updateWidgets(self, ports, portStatus, moveStatus, posZ, posT, autoMode, repeatMode):
        # print("updateWidgets() method called from MotorControllerFrame")
        # Not in Use # ???
        
        self.btConnect.updateStatus( portStatus )
        self.ltCOM.updateStatus( portStatus )
        self.listCOM.updateStatus( portStatus, ports )

        self.btRepeat.updateStatus(repeatMode) # Does not depend on motor controller
        
        if portStatus == 1:
            # self.btConnect.updateStatus( portStatus )
            self.btMove.updateStatus( portStatus )
            self.btStop.updateStatus( portStatus )
            self.btCalibrate.updateStatus( portStatus )
            self.ltActive.updateStatus( moveStatus )
            self.enPositionZ.setData( '{:.1f}'.format(posZ) )
            self.enPositionT.setData( '{:.1f}'.format(posT) )
            self.updatePlot( {'z':posZ,'t':posT} )
            self.btAuto.updateStatus(autoMode)
        else:
            self.btMove.updateStatus( 0 )
            self.btStop.updateStatus( 0 )
            self.btCalibrate.updateStatus( 0 )
            self.ltActive.updateStatus( 0 )
            self.enPositionZ.setData( 'n/a' )
            self.enPositionT.setData( 'n/a' )
            self.btAuto.updateStatus(0)
        
        
        
        if autoMode == 1: # If in Auto Mode
            # Remove ability to move
            self.btMove.updateStatus( 0 )
            self.btStop.updateStatus( 0 )
            self.btCalibrate.updateStatus( 0 )
            
            
        
    def initPlotFrame(self):
        print("initPlotFrame() method called from MotorControllerFrame")
        dir = Directory().images
        try: 
            # self.sideView = tk.PhotoImage(file = dir+'\\side_view.ppm' )
            # self.sideArm = tk.PhotoImage(file = dir + '\\sidearm.png' )
            # self.angleView = tk.PhotoImage(file = dir + '\\angle_view.ppm' )
            self.sideView = ImageTk.PhotoImage( Image.open( dir+'\\side_view.ppm').resize((540,270)) )
            self.angleView = ImageTk.PhotoImage( Image.open( dir+'\\angle_view.ppm').resize((270,270)) )
            self.sideArm = ImageTk.PhotoImage( Image.open( dir+'\\sidearm.png').resize((540,270)) )
            w = self.sideView.width() + self.angleView.width()
            h = self.sideView.height()
            print('diagram  size is ', self.sideView.width(), ', ', self.angleView.width()," x ", self.sideView.height() )
            self.diagram = tk.Canvas( self.frPlot, width = w, height = h )#self.frPlot['width'], height = self.frPlot['height'] )
            self.diagram.create_image(0,0, anchor = 'nw', image = self.sideView)
            self.diagram.addtag_all("SideImage")
            # Probe Arm
            self.diagram.create_image(0, 0, anchor = 'nw', image = self.sideArm)
            self.diagram.addtag_above("SideArm", "SideImage")   
            # Background Angle View
            self.diagram.create_image(540, 0, anchor='nw', image = self.angleView) 
            self.diagram.addtag_above("AngleImage", "SideArm") 
            
            
            self.diagram.grid( row = 0, column = 0 )
            
            
            self.a_x1 = 675
            self.a_y1 = 214#.2
            # Create Position calc. functions
            self.side_x = lambda x : -2.285*x + 453
            self.angle_x = lambda theta : self.a_x1 + 90*np.sin(np.deg2rad(theta))
            self.angle_y = lambda theta : self.a_y1 - 90*np.cos(np.deg2rad(theta))
            
            self.diagram.create_line(self.a_x1, self.a_y1, self.angle_x(0), self.angle_y(0))
            self.diagram.addtag_above("AngleArm", "AngleImage")
            
        except Exception as e:
            print(e)
            
    def setMoveParams(self, dataZ, dataT):
        self.enInputZ(dataZ)
        self.enInputT(dataT)
            
    def getParameters(self, data):
        if self.validateParameters():
            print("Validation Complete")
            self.enStatus.setData("Validation Complete")
        else:
            print("Failed Validation")
            self.enStatus.setData("Error in Validation")
            return False
        params = {}
        params = self.getValueFromSet( self.enZFields, params, 'Z', data['Motor Z'] )
        params = self.getValueFromSet( self.enTFields, params, 'T', data['Motor T'] )
        print(params)
            
        return params
    
    def validateParameters(self):        
        # Check types
        if not (self.validateSetTypes( self.enZFields ) and self.validateSetTypes( self.enTFields )):# and self.validateSetTypes( self.enBiasFields ) and self.validateSetTypes( self.enPressureFields )) == 0:
            print("Could not validate all params")
            return False
        
        # Check ranges
        # Z
        if self.enZFields['Min'].getData() != '':
            if float(self.enZFields['Min'].getData()) < self.minZScan or float(self.enZFields['Min'].getData()) > self.maxZScan:
                print("Z Minimum value ", self.enZFields['Min'].getData(), " is out of bounds (10,180)" )
                # self.enStatus.setData("Valid'n fail: Zmin beyond (10,180)" )
                return False
        if self.enZFields['Max'].getData() != '':
            if float(self.enZFields['Max'].getData()) < self.minZScan or float(self.enZFields['Max'].getData()) > self.maxZScan:
                print("Z Maximum value ", self.enZFields['Max'].getData(), " is out of bounds (10,180)" )
                return False
        # T
        if self.enTFields['Min'].getData() != '':
            if float(self.enTFields['Min'].getData()) < -60 or float(self.enTFields['Min'].getData()) > 60:
                print("T Minimum value ", self.enTFields['Min'].getData(), " is out of bounds (-60,60)" )
                return False
        if self.enTFields['Max'].getData() != '':
            if float(self.enTFields['Max'].getData()) < -60 or float(self.enTFields['Max'].getData()) > 60:
                print("T Maximum value ", self.enTFields['Max'].getData(), " is out of bounds (-60,60)" )
                return False

        return True
    
    def getValueFromSet(self, fields, params, name, existingData):
        if fields['Min'].getData() == '' and fields['Max'].getData() == '':
            params[name] = np.array([existingData])
        elif fields['Max'].getData() == '' or fields['Min'].getData() == '':
            params[name] = np.array([float(fields['Max'].getData() + fields['Min'].getData())])
        elif fields['Min'].getData() != '' and fields['Max'].getData() == fields['Min'].getData():
            params[name] = np.array( [float(fields['Min'].getData())] )
        else:
            params[name] = np.linspace( float(fields['Min'].getData()), float(fields['Max'].getData()), int(fields['Num'].getData()) )
    
        return params
    
    def validateSetTypes(self, fields):
        # first, check that all values are either empty or floatable
        try:
            for key in fields.keys():
                if fields[key].getData() != '':
                    float(fields[key].getData())
        except ValueError:
            print("Populated Fields are not all floatable")
            return False
        print("all fields are floatable, check")
        # Second, check that num is a positive non-zero integer
        try:
            if int(fields['Num'].getData()) < 1:
                raise ValueError("Number must be positive non-zero integer")
        except:
            print("Number must be positive non-zero integer")
            return False
        print("all num fields are positive non-zero int")
        # Next, check for valid max/min entries if not sweeping
        if fields['Num'].getData() == '1':
            if fields['Min'].getData() != '' and fields['Max'].getData() != '':
                if fields['Min'].getData() != fields['Max'].getData():
                    print("Max/Min cannot be inequal if not sweeping.")
                    return False
            
            return True
        else: 
            pass
        # Check for acceptable max/min entries if sweeping
            # try: 
            #     if float(fields['Max'].getData()) > float(fields['Min'].getData()):
            #         print(" max is greater than min, check.")
            #         return True
            # except:
            #     print("Maximum value must exceed minimum")
            #     return False
        return True
            
    def updatePlot(self, positions):
        # print('updating plot...')
        try:
            if positions['z'] != self.oldPositions['z']:
                self.x = self.side_x( positions['z'] )
                self.diagram.coords("SideArm", self.x, 0)
                self.oldPositions['z'] = positions['z']
            
            if positions['t'] != self.oldPositions['t']:
                self.diagram.coords("AngleArm", self.a_x1, self.a_y1, self.angle_x(positions['t']), self.angle_y(positions['t']))
                self.oldPositions['t'] = positions['t']
        except Exception as e:
            print("couldn't update plot; exception ", e)

    def testInitBtConnect(self): # Not a real method - for debug only
        print("testInitBtConnect() method called in MCFrame from View frame")
        # self.btConnect = ConnectButton(self, 'MC Connect Button')
        # self.btConnect.initButton( activeCommand, idleCommand)
        self.btConnect.name = 'name 2'
        self.btConnect.initButton( 'notACmd', "alsoNotACmd")
        
        self.btConnect.pack()
        