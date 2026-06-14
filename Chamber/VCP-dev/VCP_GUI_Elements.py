import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from misc import Directory
import math


class ClickButton( ttk.Button ):
    #Constructor
    def __init__(self, parent, name ):
        super().__init__(parent)
        self.name = name
        self.status = 0
        self.setNeutral()
        
        
    def setNeutral(self): # relief = flat, state = disabled; status = 0, don't change text(?)
        # print(" button " + self.name + ' set to neutral')
        # self['relief'] = 'flat'
        self['style'] = 'Raised.TButton'
        self.state(['disabled'])
        self.status = 0
        
    def setActive(self):
        self['style'] = 'Raised.TButton'
        self.state(['!disabled'])
        self.status = 1
        
    def initButton(self, command, label):
        # print("click button init'd for ", self.name)
        self['text'] = label
        self['command'] = command
        # self['width'] = len(label) + 2
        # self.setNeutral()
        self.setActive()
        
    def updateStatus(self, newStatus):
        # self.setNeutral()
        if( self.status == newStatus ):   # does not require button redraw if nothing changed
            # print(self.name + " skipping update")
            return
        
        # Redraw button based on new status
        if( newStatus == 1):
            self.setActive()
        else:
            self.setNeutral()
        self.status = newStatus # to preserve -1, 0.5 statuses?

class PushButton( ClickButton ):
    # For connect, output., filament buttons; has methods for setting appearance
    
    #Constructor
    def __init__(self, parent, name ):
        super().__init__(parent, name)
        
    def initButton(self, activeCommand, deactiveCommand, activeLabel, deactiveLabel):
        # print("push button init'd for ", self.name,", deactive label is", deactiveLabel)
        self.activeLabel = activeLabel
        self.activeCommand = activeCommand
        self.idleCommand = deactiveCommand    # may change 'idle' to 'deactive' for consistency
        self.idleLabel = deactiveLabel
        self['text'] = deactiveLabel
        
        # if '\n' in activeLabel:
        #     self['width'] = round(len(activeLabel)/2) + 2
        # else:
        #     # if len(activeLabel) > 10:
        #     self['width'] = len(activeLabel)
            # else:
                # self['width'] = len(activeLabel) 
        # self.setActive()
        self.setNeutral()
        
    
    def setActive(self): # sunken relief, state = active, text = activeLabel, command = ; status = 1
        # self['relief'] = 'sunken'
        self['style'] = 'Sunken.TButton'
        self['command'] = self.activeCommand
        self.state(['!disabled'])
        self['text'] = self.activeLabel
        self.status = 1
    
    def setDeactive(self): # raised relief, state = active, text = deactiveLabel, command = idleCommand; status = -1
        # print( self.name,  ' set to deactive (raised)')
        # self['relief'] = 'raised'
        self['style'] = 'Raised.TButton'
        self['command'] = self.idleCommand
        self.state(['!disabled'])
        self['text'] = self.idleLabel
        self.status = -1
    
    def updateStatus(self, newStatus):
        # self.setActive()
        if( self.status == newStatus ):   # does not require button redraw if nothing changed
            # print( self.name, " has no need to update. (new status ", newStatus, ", old is ", self.status)
            pass
        
        # Redraw button based on new status
        if( newStatus == 1):
            self.setActive()
        elif( newStatus == -1 ):
            self.setDeactive()
        elif( newStatus == 0 or newStatus == 0.5 ):
            self.setNeutral()
        else:
            print("button " + self.name + " breaks on update! please help")
            


class ConnectButton( PushButton ):
    #Constructor
    def __init__( self, parent, name ):
        super().__init__( parent, name)
        
    def initButton(self, activeCommand, idleCommand):
        super().initButton( activeCommand, idleCommand, activeLabel = "Disconnect", deactiveLabel = "Connect" )
        



class StatusLight( ttk.Button ):
    #Constructor
    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name
        self.status = 0.0
        self['style'] = 'Light.TButton'
        self.state(['readonly'])
        # img = img.resize((20, 20))
        try:
            # print('trying')
            dir = Directory().images
            # print(dir)
            # Image.open( dir+'\green_light.png' )
            self.green = ImageTk.PhotoImage( Image.open( dir+'\\green_light.png').resize((20,20)) )
            self.red = ImageTk.PhotoImage( Image.open( dir+'\\red_light.png').resize((20,20)) )
            self.yellow = ImageTk.PhotoImage( Image.open( dir+'\\yellow_light.png').resize((20,20)) )
            self.blank = ImageTk.PhotoImage( Image.open( dir+'\\blank_light.png').resize((20,20)) )
        except Exception as e:
            print(e)
            print("unable to load status light images")
        self.setNeutral()
        
        
    def setGreen(self): # status +1.0
        # print('setGreen method called')
        self.status = 1
        self['image'] = self.green
        
    def setRed(self):  # status = -1.0
        self.status = -1
        self['image'] = self.red
    
    def setYellow(self):  #status = 0.5
        self.status = 0.5
        self['image'] = self.yellow
    
    def setNeutral(self): # status = 0.0
        self.status = 0
        self['image'] = self.blank
    
    def updateStatus( self, newStatus ):
        if( self.status == newStatus ):   # does not require light redraw if nothing changed
            return
        
        # Redraw light based on new status
        if( newStatus == 1):
            self.setGreen()
        elif( newStatus == 0.5 ):
            self.setYellow()
        elif( newStatus == 0):
            self.setNeutral()
        elif( newStatus == -1 ):
            self.setRed()        
        else:
            print("button " + self.name + " breaks on update! please help")

class SelectorBox( ttk.Combobox ):
    #Constructor
    def __init__(self, parent, name):
        super().__init__(parent) # textVar is a tk.StringVar()
        self.name = name
        self.status = 1
        self['values'] = ""
        self['textvariable'] = None
        self.state(['readonly'])
        self['width'] = 6
        
    def lock( self):
        self.state(['disabled'])
    
    def unlock(self):
        self.state(['!disabled'])
        
    def setSelection(self, setValue):
        # print("setSelection() method called from " + self.name + " Box")
        self.set( setValue )
        
    def getSelection(self):
        # print("getSelection() method called from " + self.name)
        return self.get()
        
    def setList( self,  availablePorts ):
        self['values'] = availablePorts
    
    def updateStatus( self, newStatus, availablePorts ):
        # print('updating list box for ', self.name)
        if( self.status == newStatus and availablePorts == self['values']):   # does not require redraw if nothing changed
            return
        
        try:
            # Redraw button based on new status
            if( newStatus == 1 or newStatus == 0.5):
                self.lock()
            else:
                self.unlock()
        except:
            print("update listbox don't work")

class PortSelectorBox( SelectorBox ):
    #Constructor
    def __init__(self, parent, name):
        super().__init__(parent, name)
        
    def updateStatus( self, newStatus, availablePorts ):
        # print('updating list box for ', self.name)
        super().updateStatus(newStatus, availablePorts)
        if( self['values'] != availablePorts ):
            self.setList( availablePorts )
            
    def getSelection(self):
        # print("getSelection() method called from " + self.name + " SelectorBox")
        # print( "COM list has value ", self.get() )
        return self.get()
    
    # def setTextVariable(self, textVar ):
    #     self['textvariable'] = textVar
    
class RampTimeBox( SelectorBox ):
    #Constructor
    def __init__(self, parent, name):
        super().__init__(parent, name) # textVar is a tk.StringVar()
        self['values'] =[ "1s", "15s", "1min", "5min", "10min", "30min" ]
        self.times = { "1s":1, "15s":15, "1min":60, "5min":300, "10min":600, "30min":1800 }
        self.set( "1s" )
   
    # def updateStatus( self, newStatus, availablePorts ):
    #     super().up
            
    def getSelection(self):
        print("getSelection() method called from " + self.name + " RampTimeBox")
        print( "Ramptime box has value ", self.times[self.get()] )
        return self.times[self.get()]

class SweepSelectorBox( SelectorBox ):
    def __init__(self, parent, name):
        super().__init__(parent, name)
        self['width'] = 10
        self.sweeps = {}
        
    def createList( self, shape, boardID ):
        self.sweeps = {}
        try:
            if boardID == 1:
                for k in range( shape[2] ):
                    self.sweeps['Sweep #{:d}'.format(k+1)] = k
                self['values'] = list(self.sweeps.keys())
            elif boardID == 2:
                for k in range( shape[2] ):
                    self.sweeps['Sweep #{:d}'.format(math.floor(k/2)+1)] = k-1
                self['values'] = list(self.sweeps.keys())
        except:
            print("Error creating list")
            
    def getSelection(self):
        return self.sweeps[self.get()]
        



class DataEntry( ttk.Entry ):   ## This takes the StringVar() as an argument!! and is init'd in view frames
    #Constructor
    def __init__(self, parent, name, editable, width):
        super().__init__(parent)
        self.name = name
        self.textVar = tk.StringVar()
        self['textvariable'] = self.textVar
        self['width'] = width
        self['justify'] = 'center'
        if editable == 0:
            self.state(['readonly'])
        self['font']  = ('Helvetica', 14)
        # self[width] 
        # add some initiatization things to make it look pretty
    
    def setData(self, newData):
        # print('setting ', self.name)
        if self.textVar.get() is not newData:
            self.textVar.set(newData)
            
    def getData(self):
        # print(self.name, 'value is ', self.get() )
        return self.get()
        
    def readOnly(self):
        self.status(['readonly'])
        
    def editable(self):
        self.status(['!readonly'])
        
    
    