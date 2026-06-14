# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 10:53:02 2024

@author: ROWANJ2
"""

import tkinter as tk
import tkinter.ttk as ttk
from VCP_GUI_Elements import *
import numpy as np

class AutomaterFrame( ttk.Frame ):
    def __init__(self, parent):
        super().__init__(parent)
        self.dvAutoProgress = tk.IntVar()
    
    
        self['borderwidth'] = 1
        self['relief'] = 'solid'
    
    def updateWidgets(self, autoMode):
        self.btAuto.updateStatus(autoMode)
        
        if autoMode == -1:
            self.dvAutoProgress.set(100)
        
    
    def initWidgets(self):
        print("initWidgets() method called from AutoFrame")
        self.frData = ttk.Frame(self)
        
        self.btAuto = PushButton(self, 'AutoStart')
        self.enStatus = DataEntry(self, 'AutoStatus', editable=False, width=32)
        
        # self.enPressureFields = {}
        # self.enPressureFields['Min'] = DataEntry(self.frData, 'PressureMin', editable=True, width=5)
        # self.enPressureFields['Max'] = DataEntry(self.frData, 'PressureMax', editable=True, width=5)
        # self.enPressureFields['Num'] = DataEntry(self.frData, 'PressureNum', editable=True, width=5)
        # self.enPressureFields['Num'].setData('1')
        
        # self.enBiasFields = {}
        # self.enBiasFields['Min'] = DataEntry(self.frData, 'BiasMin', editable=True, width=5)
        # self.enBiasFields['Max'] = DataEntry(self.frData, 'BiasMax', editable=True, width=5)
        # self.enBiasFields['Num'] = DataEntry(self.frData, 'BiasNum', editable=True, width=5)
        # self.enBiasFields['Num'].setData('1')
        
        self.enZFields = {}
        self.enZFields['Min'] = DataEntry(self.frData, 'ZMin', editable=True, width=5)
        self.enZFields['Max'] = DataEntry(self.frData, 'ZMax', editable=True, width=5)
        self.enZFields['Num'] = DataEntry(self.frData, 'ZNum', editable=True, width=5)
        self.enZFields['Num'].setData('1')
        
        self.enTFields = {}
        self.enTFields['Min'] = DataEntry(self.frData, 'TMin', editable=True, width=5)
        self.enTFields['Max'] = DataEntry(self.frData, 'TMax', editable=True, width=5)
        self.enTFields['Num'] = DataEntry(self.frData, 'TNum', editable=True, width=5)
        self.enTFields['Num'].setData('1')
        
        self.pbProgress = ttk.Progressbar( self, orient=tk.HORIZONTAL, length = 100, mode='determinate', variable=self.dvAutoProgress, style="bar.Horizontal.TProgressbar")
        
        self.initLabels()
        self.initLocations()
        
        
    def initLabels(self):
        self.lblTitle = ttk.Label(self, text = 'Motor Scan', style = 'Std.TLabel' )
        
        
        # self.lblPlaceholder = ttk.Label(self.frData, text='<Placeholder>', style = 'Std.TLabel')
        # self.lblPressureRange = ttk.Label(self.frData, text='Pressure:', style = 'Std.TLabel')
        # self.lblBiasRange = ttk.Label(self.frData, text='Bias:', style = 'Std.TLabel')
        self.lblZRange = ttk.Label(self.frData, text='Distance:', style = 'Std.TLabel')
        self.lblTRange = ttk.Label(self.frData, text = "Angle:", style = 'Std.TLabel')
        
        self.lblMin = ttk.Label(self.frData, text = 'Min', style = 'Std.TLabel' )
        self.lblMax = ttk.Label(self.frData, text = 'Max', style = 'Std.TLabel' )
        self.lblNum = ttk.Label(self.frData, text = '# Points', style = 'Std.TLabel' )
        
        
        self.lblStatus = ttk.Label(self, text='Status:', style = 'Std.TLabel')

        
        # self.lblSetpoint = ttk.Label(self.frData, text = 'Setpoint:', style = 'Std.TLabel' )
        # self.lblInput = ttk.Label( self.frData, text = 'Input Set V:', style = 'Std.TLabel' )
        # self.lblUnit1 = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
        # self.lblUnit2 = ttk.Label( self.frData, text = 'V', style = 'Std.TLabel' )
    
    def initLocations(self):
        print("initializing widgets & placement for Auto frame" )
        self.columnconfigure( index=0, weight=3 )
        self.columnconfigure( index=1, weight=1 )
        self.columnconfigure( index=2, weight=1 )
        self.columnconfigure( index=3, weight=1 )
        self.rowconfigure( index=0, weight=0 )
        self.rowconfigure( index=1, weight=4)
        self.rowconfigure( index=2, weight=1)
        self.rowconfigure( index=3, weight=1)
        self.rowconfigure( index=4, weight=0)
        self.rowconfigure( index=5, weight=1)
        self['padding'] = ('0.1c', '0.1c')
        
        self.lblTitle.grid(row = 0, column = 0, columnspan =3)
        
        self.frData.grid(row = 1, column = 0, columnspan = 3, sticky = 'nsw')
        self.frData.columnconfigure( index=0, weight=1 )
        self.frData.columnconfigure( index=1, weight=1 )
        self.frData.columnconfigure( index=2, weight=1 )
        self.frData.columnconfigure( index=3, weight=0 )
        # self.frData.columnconfigure( index=1, weight=1 )
        # self.frData.columnconfigure( index=2, weight=1 )
        self.frData.rowconfigure( index=0, weight=1 )
        self.frData.rowconfigure( index=2, weight=1 )
        self.frData.rowconfigure( index=4, weight=1 )
        self.frData.rowconfigure( index=6, weight=1 )
        
        self.frData['padding'] = ('0.1c', '0.1c')
        # self.lblPlaceholder.grid(row = 0, column = 0, sticky='nesw')
        pad = 7
        self.lblMin.grid(row = 0, column = 1)
        self.lblMax.grid(row = 0, column = 2)
        self.lblNum.grid(row = 0, column = 3)
        
        self.lblZRange.grid(row = 1, column = 0, sticky = 'e')
        self.enZFields['Min'].grid( row = 1, column = 1, padx = pad )
        self.enZFields['Max'].grid( row = 1, column = 2, padx = pad )
        self.enZFields['Num'].grid( row = 1, column = 3, padx = pad )
        
        self.lblTRange.grid( row = 3, column = 0, sticky = 'e')
        self.enTFields['Min'].grid( row = 3, column = 1 )
        self.enTFields['Max'].grid( row = 3, column = 2 )
        self.enTFields['Num'].grid( row = 3, column = 3 )
        
        # self.lblBiasRange.grid( row = 5, column = 0, sticky = 'e' )
        # self.enBiasFields['Min'].grid( row = 5, column = 1 )
        # self.enBiasFields['Max'].grid( row = 5, column = 2 )
        # self.enBiasFields['Num'].grid( row = 5, column = 3 )
        
        # self.lblBiasRange.grid( row = 7, column = 0, columnspan = 2, sticky = 'e' )
        # self.enFields['BiasMin.grid( row = 8, column = 0 )
        # self.enFields['BiasMax.grid( row = 8, column = 1 )
        # self.enFields['BiasNum.grid( row = 8, column = 2 )
        
        # self.lblPressureRange.grid( row = 7, column = 0, sticky = 'e' )
        # self.enPressureFields['Min'].grid( row = 7, column = 1 )
        # self.enPressureFields['Max'].grid( row = 7, column = 2 )
        # self.enPressureFields['Num'].grid( row = 7, column = 3 )
        
        
        self.lblStatus.grid(row = 2, column = 0)
        self.enStatus.grid(row = 3, column = 0, columnspan = 3)
        self.pbProgress.grid(row = 4, column = 0, columnspan=3, sticky='ew')
        self.btAuto.grid(row = 5, column = 0, columnspan = 3, sticky='ew')
        
        
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
        # params = self.getValueFromSet( self.enBiasFields, params, 'Bias', data['Bias Setpoint'] )
        # params = self.getValueFromSet( self.enPressureFields, params, 'Pressure', data['Pressure'] )
        print(params)
        # if self.enZFields['Num'].getData() == '1': # Take whichever value is present, else, 
            
        return params
        
        
        
    def validateParameters(self):        
        # Check types
        if (self.validateSetTypes( self.enZFields ) and self.validateSetTypes( self.enTFields )):# and self.validateSetTypes( self.enBiasFields ) and self.validateSetTypes( self.enPressureFields )) == 0:
            return False
        
        # Check ranges
        # Z
        if self.enZFields['Min'].getData() != '':
            if float(self.enZFields['Min'].getData()) < 10 or float(self.enZFields['Min'].getData()) > 180:
                print("Z Minimum value ", self.enZFields['Min'].getData(), " is out of bounds (10,180)" )
                self.enStatus.setData("Valid'n fail: Zmin beyond (10,180)" )
                return False
        if self.enZFields['Max'].getData() != '':
            if float(self.enZFields['Max'].getData()) < 10 or float(self.enZFields['Max'].getData()) > 180:
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
            
        # # Bias
        # if self.enBiasFields['Min'].getData() != '':
        #     if float(self.enBiasFields['Min'].getData()) <  0 or float(self.enBiasFields['Min'].getData()) > 80:
        #         print("Bias Minimum value ", self.enBiasFields['Min'].getData(), " is out of bounds (0,80)" )
        #         return False
        # if self.enBiasFields['Max'].getData() != '':
        #     if float(self.enBiasFields['Max'].getData()) < 0 or float(self.enBiasFields['Max'].getData()) > 80:
        #         print("Bias Maximum value ", self.enBiasFields['Max'].getData(), " is out of bounds (0,80)" )
        #         return False
            
        # # Pressure
        # if self.enPressureFields['Min'].getData() != '':
        #     if float(self.enPressureFields['Min'].getData()) < 1e-5 or float(self.enPressureFields['Min'].getData()) > 1e-3:
        #         print("Pressure Minimum value ", self.enPressureFields['Min'].getData(), " is out of bounds (1e-5,1e-3)" )
        #         return False
        # if self.enPressureFields['Max'].getData() != '':
        #     if float(self.enPressureFields['Max'].getData()) < 1e-5 or float(self.enPressureFields['Max'].getData()) > 1e-3:
        #         print("Pressure Maximum value ", self.enPressureFields['Max'].getData(), " is out of bounds (1e-5,1e-3)" )
        #         return False

        return True
    
    def getValueFromSet(self, fields, params, name, existingData):
        # if fields['Num'].get() == '1':
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
        # flag = False
        
        
        # first, check that all values are either empty or floatable
        try:
            for key in fields.keys():
                if fields[key].getData() != '':
                    float(fields[key].getData())
        except ValueError:
            print("Populated Fields are not all floatable")
            return False
        
        # Second, check that num is a positive non-zero integer
        try:
            if int(fields['Num'].getData()) < 1:
                raise ValueError("Number must be positive non-zero integer")
        except:
            print("Number must be positive non-zero integer")
            return False
        
        # Next, check for valid max/min entries if not sweeping
        if fields['Num'].getData() == '1':
            if fields['Min'].getData() != '' and fields['Max'].getData() != '':
                if fields['Min'].getData() != fields['Max'].getData():
                    print("Max/Min cannot be inequal if not sweeping.")
                    return False
                    
            return True
        
        else: 
        # Check for acceptable max/min entries if sweeping
            try: 
                # if fields['Min'].getData() != '' and fields['Max'].getData() != '' and fields['Max'].getData() != fields['Min'].getData():
                #     print("Max cannot be different from Min with Num = 1")
                #     return False
                
                if float(fields['Max'].getData()) > float(fields['Min'].getData()):
                    return True
            except:
                print("Maximum value must exceed minimum")
                return False
        
        # return flag