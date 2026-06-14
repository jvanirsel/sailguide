''' 
Created on Oct 22, 2025
Seth Gerow
Senior Design Project 
'''
import tkinter as tk
import tkinter.ttk as ttk
from VCP_GUI_Elements import *
from RPA import RPA
import serial as s
from serial.tools.list_ports import comports
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as md
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from time import sleep
from threading import Thread
from RPAconstants import *
import re
import numpy as np
import time
import os
import scipy.io as sio
from collections import defaultdict

class RPAFrame( ttk.Frame ):
    # copy of tkinter frame template
    def __init__(self, parent, windows = True):
        super().__init__(parent)
        self.windows = windows #if false, the RPA frame will hold all widgets in a single frame
        # if true, the RPA Frame will allow for the calibration, plot, and configuration windows 
        # to be opened in separate windows, true is default setting for vcp

        self['borderwidth'] = 1
        self['relief'] = 'solid'
        
        ## Windows ##
        self.winPlot = subWindow(parent, self, windows)
        self.winConfig = subWindow(parent, self, windows)
        self.winCalibrate = subWindow(parent, self, windows)
        
        self.showCal = not windows
        self.showPlot = not windows
        self.showParams = not windows
        
        self.slow_history = defaultdict(list)

    def updateWidgets(self, ports, portStatus, outputStatus, rpaData, rpaSupportData):
        current = rpaData['current']
        voltage = rpaData['voltage']
        temp = rpaData['temp']
        density = rpaData['density']
        velocity = rpaData['velocity']
        adc_counts = rpaData['adc_counts'][-1]
        dac_counts = rpaData['dac_counts'][-1]
        current_array = rpaData['current_array']
        voltage_array = rpaData['voltage_array']
        
        self.btConnect.updateStatus( portStatus )
        self.ltCOM.updateStatus( portStatus )
        self.listCOM.updateStatus( portStatus, ports )
        self.ltSweeping.updateStatus( outputStatus)
        if portStatus == 1:
            self.bttakeSweep.updateStatus(1)
            self.Current.setData(current)
            self.Voltage.setData(voltage)
            self.ionTemperature.setData(temp)
            self.ionDensity.setData(density)
            self.ionVelocity.setData(velocity)
            if self.showCal:
                self.ADCcountsoutput.setData(adc_counts)
            if self.showPlot:
                self.updatePlots(voltage_array, current_array)
            if rpaSupportData['needSave'] ==1:
                self.savetoFile(rpaData, rpaSupportData)
        else:
            self.bttakeSweep.updateStatus(0)
            
    def updatePlots(self, voltage_array, current_array):
        self.ax1.clear()
        self.ax2.clear()
        for sweep_id in current_array:
            #print(sweep_id)
            if sweep_id in voltage_array:
                self.ax1.plot(voltage_array[sweep_id], current_array[sweep_id], label = f'Sweep {sweep_id}', linewidth = 1)
        #if self.ltSweeping.status == -1:
        num_sweeps = 0
        if len(current_array) == len(voltage_array):
            num_sweeps = len(current_array) 
        if num_sweeps:
            min_len = min(len(v) for v in voltage_array.values())

            voltage_avg = np.mean([v[:min_len] for v in voltage_array.values()], axis=0)
            current_avg = np.mean([c[:min_len] for c in current_array.values()], axis=0)
            self.ax2.plot(voltage_avg, current_avg, label = 'Averaged Sweep', linewidth = 1) 
        self.ax1.set_title('IV curve')
        self.ax1.set_xlabel('V (V)')
        self.ax1.set_ylabel('I (nA)')
        self.ax2.set_title('IV curve (avgs)')
        self.ax2.set_xlabel('V (V)')
        self.ax2.set_ylabel('I (nA)')
        self.ax1.set_xlim([-5,12])
        self.ax2.set_xlim([-5,12])
        if num_sweeps:
            self.ax1.set_ylim([np.min(current_avg)-10,np.max(current_avg)+10])
            self.ax2.set_ylim([np.min(current_avg)-10,np.max(current_avg)+10])
            self.ax1.legend()
            self.ax2.legend()
        self.canvas.draw()
        
    def savetoFile(self, RPAData, SupportData):
        filename = self.sweepFileName.getData()
        if not filename:
            filename = 'Sweep.mat'
        filepath = SupportData['savefile']
        filename = filepath / filename

        # flatten nested dict structure into parallel arrays
        sweep_nums, point_ids, voltages, currents = [], [], [], []
        adc_counts, dac_counts, temps, velocities, densities = [], [], [], [], []

        for sweep_num, array in RPAData['sweep_num'].items():
            sweep_nums.extend(array)
        for sweep_num, array in RPAData['point_id'].items():
            point_ids.extend(array)
        for sweep_num, array in RPAData['voltage_array'].items():
            voltages.extend(array)
        for sweep_num, array in RPAData['current_array'].items():
            currents.extend(array)
        for sweep_num, array in RPAData['adc_counts'].items():
            adc_counts.extend(array)
        for sweep_num, array in RPAData['dac_counts'].items():
            dac_counts.extend(array)
#        for sweep_num, array in RPAData['temp'].items():
#            temps.extend(array)
#        for sweep_num, array in RPAData['velocity'].items():
#            velocities.extend(array)
#        for sweep_num, array in RPAData['density'].items():
#            densities.extend(array)

        # build the flat data dict
        data = {
            'sweep_num':  np.array(sweep_nums),
            'point_id':   np.array(point_ids),
            'voltage':    np.array(voltages),
            'current':    np.array(currents),
            'dac_counts': np.array(dac_counts),
            'adc_counts': np.array(adc_counts),
            'temp':       np.array(temps),
            'velocity':   np.array(velocities),
            'density':    np.array(densities),
        }

        total_len = len(data['sweep_num'])

        # record current slow data values at their position in the fast array
        for key, value in SupportData.items():
            if key in ('savefile', 'needSave'):
                continue
            self.slow_history[key].append((total_len - 1, value))

        # rebuild slow arrays from history every save
        for key, entries in self.slow_history.items():
            arr = np.full(total_len, np.nan, dtype=float)
            for index, value in entries:
                if index < total_len:
                    arr[index] = value
            data[key] = arr

        print(f'saving to {filename}...')
        try:
            sio.savemat(filename, data)
            print(f'saved successfully to {filename}')
        except Exception as e:
            print(f'save failed: {e}')
        

    def initWidgets(self):
        print("initWidgets() method called for RPAFrame")
        ## Frames ##
        self.frMain = ttk.Frame(self) # stores the COM parameters, and main buttons
        self.frCOM = ttk.Frame(self.frMain) #frame for COM port selection
        self.frParams = ttk.Frame(self.winConfig.window) #frame for RPA parameters
        self.frPlot = ttk.Frame(self.winPlot.window) #frame for RPA plot
        self.frData = ttk.Frame(self.frMain) #frame for RPA data display
        self.frCal = ttk.Frame(self.winCalibrate.window) #frame for calibration options
        self.frButtons = ttk.Frame(self.frMain) #frame for normal buttons

        ## Buttons and Data Entries ##
        self.listCOM = PortSelectorBox( self.frCOM, 'RPA' ) #COM port selector
        self.btConnect = ConnectButton( self.frCOM, 'RPAconnect') #connect button
        self.ltCOM = StatusLight( self.frCOM, 'RPAcom' ) #COM status light
        self.ltSweeping = StatusLight(self.frCOM, 'RPAsweeping') #Sweeping status light
        self.bttakeSweep = PushButton(self.frButtons, 'RPAdosweep') #do a sweep, or stop a sweep
        self.btshowPlot = ClickButton(self.frButtons, 'RPAopenplot') #open plot window button
        self.bteditParams = ClickButton(self.frButtons, 'RPAparams') #open params window
        self.btcalibrate = ClickButton(self.frButtons, 'RPACalibrate')

        ## RPA calibration stuff ##
        self.ADCcountsoutput = DataEntry(self.frCal, 'ADC counts', False, 5)
        self.DACcountsinput = DataEntry(self.frCal, 'DAC counts', True, 5)
        self.ADCcurrinput = DataEntry(self.frCal, 'ADC input current', True, 5)
        self.DACvoltoutput = DataEntry(self.frCal, 'DAC output voltage', True, 5)
        self.DACcalfilename = DataEntry(self.frCal, 'DAC calibration filename', True, 15)
        self.ADCcalfilename = DataEntry(self.frCal, 'ADC calibration filename', True, 15)
        self.numADCreads = DataEntry(self.frCal, 'num ADC reads', True, 5)
        self.btADCread = ClickButton(self.frCal, 'get ADC readings')
        self.btDACread = ClickButton(self.frCal, 'get DAC readings')
        self.btsaveDACpoint = ClickButton(self.frCal, 'save DAC point')

        ## Sweep Parameters ##
        self.sweepStartVolt = DataEntry(self.frParams, 'Sweep Start', True, 5)
        self.sweepEndVolt = DataEntry(self.frParams, 'Sweep End', True, 5)
        self.sweepSteps = DataEntry(self.frParams, 'Sweep Steps', True, 5)
        self.sweepDelay = DataEntry(self.frParams, 'Sweep Delay', True, 5)
        self.sweepAvg = DataEntry(self.frParams, 'Sweep Averages', True, 5)
        self.numSweeps = DataEntry(self.frParams, 'Number of Sweeps', True, 5)
        self.sweepMode = DataEntry(self.frParams, 'Sweep Mode', True, 5)
        self.sweepFileName = DataEntry(self.frParams, 'Sweep File', True, 15)
        self.btConfigureSweep = ClickButton(self.frParams, 'confgiure sweep command')
        self.btSetSaveDir = ClickButton(self.frParams, 'set save directory')


        ## Sweep Data ##
        self.Current = DataEntry(self.frData, 'RPA Current', False, 5)
        self.Voltage = DataEntry(self.frData, 'RPA Voltage', False, 5)
        self.ionTemperature = DataEntry(self.frData, 'ion Temperature', False, 5)
        self.ionDensity = DataEntry(self.frData, 'ion Density', False, 5)
        self.ionVelocity = DataEntry(self.frData, 'ion Velocity', False, 5)
        self.Current.setData(0)
        self.Voltage.setData(0)
        self.ionTemperature.setData(0)
        self.ionDensity.setData(0)
        self.ionVelocity.setData(0)
        
        self.sweepStartVolt.setData('0x0000')
        self.sweepEndVolt.setData('0xFFFF')
        self.sweepSteps.setData(1024)
        self.sweepDelay.setData(5)
        self.sweepAvg.setData(255)
        self.sweepMode.setData('manual')
        
        self.initLabels()
        self.initLocations()
        self.initPlotFrame()

    def initLabels(self):
        print("initLabels() method called for RPAFrame")
        ## COM frame labels ##
        self.lblTitle = ttk.Label(self.frMain, text = 'RPA', style = 'Header.TLabel' )
        self.lblCOMPort = ttk.Label( self.frCOM, text = 'COM Port:', style = 'Std.TLabel' )
        self.lblCOMStatus = ttk.Label( self.frCOM, text = 'COM Status', style = 'Std.TLabel' )
        self.lblOpenConfig = ttk.Label(self.frCOM, text = 'Open Config', style = 'Std.TLabel')
        self.lblOpenPlot = ttk.Label(self.frCOM, text = 'Open Plot', style = "Std.TLabel")
        self.lblSweepingStatus = ttk.Label(self.frCOM, text = 'Sweep Status', style= 'Std.TLabel')

        ## Sweep params labels ##
        self.lblparamsheader = ttk.Label(self.frParams, text = 'Sweep Parameters', style='Std.TLabel')
        self.lblstartvolt = ttk.Label(self.frParams, text= 'Start Voltage (V)', style = 'Std.TLabel')
        self.lblendvolt = ttk.Label(self.frParams, text= 'End Voltage (V)', style = 'Std.TLabel')
        self.lblsteps = ttk.Label(self.frParams, text= '# Steps/Sweep', style = 'Std.TLabel')
        self.lbldelay = ttk.Label(self.frParams, text= 'Delay/Step (ms)', style = 'Std.TLabel')
        self.lblavg = ttk.Label(self.frParams, text= '# Points/Sample', style = 'Std.TLabel')
        self.lblnumsweeps = ttk.Label(self.frParams, text = '# Sweeps', style='Std.TLabel')
        self.lblsweepmode = ttk.Label(self.frParams, text = "Sweep Mode\n['idle', 'rapid', 'manual']", style='Std.TLabel')
        self.lblsweepfile = ttk.Label(self.frParams, text = "Filename", style='Std.TLabel')

        ## main display "last sweep" output labels
        self.lblcurrent = ttk.Label(self.frData, text= 'I', style = 'Std.TLabel')
        self.lblvolt = ttk.Label(self.frData, text= 'V', style = 'Std.TLabel')
        self.lbltemperature = ttk.Label(self.frData, text= 'T', style = 'Std.TLabel')
        self.lbldensity = ttk.Label(self.frData, text= 'n', style = 'Std.TLabel')
        self.lblvelocity = ttk.Label(self.frData, text= 'u', style = 'Std.TLabel')

        self.lblnanoA = ttk.Label(self.frData, text= 'nA', style = 'Std.TLabel')
        self.lblV = ttk.Label(self.frData, text= 'V', style = 'Std.TLabel')
        self.lblV2 = ttk.Label(self.frParams, text= 'V', style = 'Std.TLabel')
        self.lbleV = ttk.Label(self.frData, text= 'eV', style = 'Std.TLabel')
        self.lblmcubed = ttk.Label(self.frData, text= 'm^-3', style = 'Std.TLabel')
        self.lblmps = ttk.Label(self.frData, text= 'm/s', style = 'Std.TLabel')
        self.lblms = ttk.Label(self.frParams, text = 'ms', style='Std.TLabel')

        ## calibration labels
        self.lblCalHeader = ttk.Label(self.frCal, text = 'Calibration', style = 'Std.TLabel')
        self.lblADCcountsoutput = ttk.Label(self.frCal, text = 'ADC Counts\nOutput', style = 'Std.TLabel')
        self.lblDACcountsinput = ttk.Label(self.frCal, text = 'DAC Counts\nInput', style = 'Std.TLabel')
        self.lblADCcurrinput = ttk.Label(self.frCal, text='ADC Current\nInput', style = 'Std.TLabel')
        self.lblDACvoltoutput = ttk.Label(self.frCal, text = 'DAC Voltage\nOutput', style = 'Std.TLabel')
        self.lblDACcalfilename = ttk.Label(self.frCal, text = 'DAC Calibration Filename', style = 'Std.TLabel')
        self.lblADCcalfilename = ttk.Label(self.frCal, text = 'ADC Calibration Filename', style = 'Std.TLabel')
        self.lblnumADCreads = ttk.Label(self.frCal, text = 'Number of ADC Readings', style = 'Std.TLabel')

    def initPlotFrame(self):
        self.fig = Figure(figsize=(10,5), dpi=100,tight_layout=True)
        self.ax1 = self.fig.add_subplot(1,2,1, polar=False)
        self.ax1.set_title('IV curve')
        self.ax1.set_xlabel('V (V)')
        self.ax1.set_ylabel('I (nA)')
        self.ax2 = self.fig.add_subplot(1,2,2, sharey= self.ax1)
        self.ax2.set_title('IV curve (avgs)')
        self.ax2.set_xlabel('V (V)')
        self.ax2.set_ylabel('I (nA)')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frPlot)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1,column=0)

    def initLocations(self):
        print("initLocations() method called for RPAFrame")
        self.frMain.grid(row=0,column=0)
        if not self.windows:
            self.winConfig.window.grid(row=0, column=1)
            self.winCalibrate.window.grid(row=0, column=2)
            self.winPlot.window.grid(row=1, column=0, columnspan=3)

        self.columnconfigure( index=0, weight=0 )
        self.rowconfigure( index=0, weight=0 )
        self.lblTitle.grid( row = 0, column = 0, columnspan=2, pady=5 ) #place title label at top
        ## COM Frame ##
        self.frCOM.grid( row = 1, column = 0, columnspan=2, padx=5, pady=5, sticky='nsew' ) #place COM frame
        self.frCOM.columnconfigure( index=0, weight=0 )
        self.lblCOMPort.grid( row = 0, column = 0, sticky='w' ) #COM Port Label
        self.listCOM.grid( row = 0, column = 1, sticky='w' ) #COM Port Selector
        self.ltCOM.grid( row = 1, column = 1, padx=5, pady=5 ) #COM Status Light
        self.lblCOMStatus.grid( row = 1, column = 0, sticky='w' ) #COM Status Label
        self.btConnect.grid( row = 0, column = 2, padx=5, pady=5 ) #COM Connect Button
        self.lblSweepingStatus.grid(row=1, column=2, sticky='w')
        self.ltSweeping.grid(row=1, column=3, padx=5, pady=5 )

        ## Params Frame ##
        self.frParams['relief'] = 'sunken'
        self.frParams['padding'] = ('0.1c', '0.1c')
        self.frParams.grid( row = 0, column = 0, padx=5, pady=5, sticky='nsew' )
        self.frParams.columnconfigure( index=0, weight=0 )
        self.lblparamsheader.grid(row=0, column = 0, columnspan=2, sticky='w')
        row_index = 1
        self.lblstartvolt.grid(row=row_index, column=0)
        self.sweepStartVolt.grid(row=row_index, column=1)
        row_index += 1
        self.lblendvolt.grid(row=row_index, column=0)
        self.sweepEndVolt.grid(row=row_index, column=1)
        row_index += 1
        self.lblsteps.grid(row=row_index, column=0)
        self.sweepSteps.grid(row=row_index, column=1)
        row_index += 1
        self.lbldelay.grid(row=row_index, column=0)
        self.sweepDelay.grid(row=row_index, column=1)
        row_index += 1
        self.lblavg.grid(row=row_index, column=0)
        self.sweepAvg.grid(row=row_index, column=1)
        row_index += 1
        self.lblnumsweeps.grid(row=row_index, column=0)
        self.numSweeps.grid(row=row_index, column=1)
        row_index += 1
        self.lblsweepmode.grid(row=row_index, column=0)
        self.sweepMode.grid(row=row_index, column=1)
        row_index += 1
        self.lblsweepfile.grid(row=row_index, column=0)
        self.sweepFileName.grid(row=row_index, column=1)
        row_index += 1
        self.btSetSaveDir.grid(row=row_index, column=0, columnspan =2)
        row_index += 1
        self.btConfigureSweep.grid(row=row_index, column=0, columnspan = 2)

        self.frData.grid(row=2, column=0, rowspan = 4,padx=5, pady=5, sticky='nsew' )
        self.frData['relief'] = 'sunken'
        self.frData['padding'] = ('0.1c', '0.1c')
        self.frData.columnconfigure(index=0, weight=0)
        row_index = 1
        self.lblcurrent.grid(row=row_index, column=0)
        self.Current.grid(row=row_index, column=1)
        self.lblnanoA.grid(row=row_index, column=2)
        row_index += 1
        self.lblvolt.grid(row=row_index, column=0)
        self.Voltage.grid(row=row_index, column=1)
        self.lblV.grid(row=row_index, column=2)
        row_index += 1
        self.lbltemperature.grid(row=row_index, column=0)
        self.ionTemperature.grid(row=row_index, column=1)
        self.lbleV.grid(row=row_index, column=2)
        row_index += 1
        self.lbldensity.grid(row=row_index, column=0)
        self.ionDensity.grid(row=row_index, column=1)
        self.lblmcubed.grid(row=row_index, column=2)
        row_index += 1
        self.lblvelocity.grid(row=row_index, column=0)
        self.ionVelocity.grid(row=row_index, column=1)
        self.lblmps.grid(row=row_index, column=2)
        
        


        self.frButtons['relief'] = 'sunken'
        self.frButtons['padding'] = ('0.1c', '0.1c')
        self.frButtons.grid( row = 2, column = 1, rowspan = 4, padx=5, pady=5, sticky='nsew' )
        self.frButtons.columnconfigure( index=0, weight=0 )
        self.btcalibrate.grid(row=0, column=0)
        self.bteditParams.grid(row=1, column=0)
        self.bttakeSweep.grid(row=2, column=0)
        self.btshowPlot.grid(row=3, column=0)

        #calibration frame
        self.frCal['relief'] = 'sunken'
        self.frCal['padding'] = ('0.1c', '0.1c')
        self.frCal.grid( row = 0, column = 0, padx=5, pady=5, sticky='nsew' )
        self.frCal.columnconfigure( index=0, weight=0 )

        self.lblCalHeader.grid(row=0, column=0, columnspan=4)
        self.lblADCcountsoutput.grid(row=1, column=2)
        self.lblDACcountsinput.grid(row=2,column=0)
        self.ADCcountsoutput.grid(row=1, column=3)
        self.DACcountsinput.grid(row=2,column=1)
        self.lblADCcurrinput.grid(row=1, column=0)
        self.lblDACvoltoutput.grid(row=2,column=2)
        self.ADCcurrinput.grid(row=1,column=1)
        self.DACvoltoutput.grid(row=2,column=3)
        self.lblDACcalfilename.grid(row=3,column=0,columnspan=2)
        self.lblADCcalfilename.grid(row=4,column=0,columnspan=2)
        self.DACcalfilename.grid(row=3, column=2, columnspan=2)
        self.ADCcalfilename.grid(row=4, column=2, columnspan=2)
        self.lblnumADCreads.grid(row = 1,column=4)
        self.numADCreads.grid(row=1, column=5)
        self.btsaveDACpoint.grid(row=2, column=4)
        self.btADCread.grid(row=3,column=4)
        self.btDACread.grid(row=4,column=4)

        self.frPlot['relief'] = 'sunken'
        self.frPlot['padding'] = ('0.1c', '0.1c')
        self.frPlot.grid( row = 0, column = 0, padx=5, pady=5, sticky='nsew' )
        self.frPlot.columnconfigure( index=0, weight=0 )

    def openPlotWindow(self):
        self.showPlot = True
        self.winPlot.show()

    def closePlotWindow(self):
        self.showPlot = False
        self.winPlot.hide()

    def openCalibrateWindow(self):
        self.showCal = True
        self.winCalibrate.show()

    def closeCalibrateWindow(self):
        self.showCal = False
        self.winCalibrate.hide()

    def openConfigureWindow(self):
        self.showParams = True
        self.winConfig.show()

    def closeConfigureWindow(self):
        self.showParams = False
        self.winConfig.hide()

class RPAcontroller():
    def __init__(self, master, rpa, rpaframe):
        self.root = master
        self.RPA = rpa
        self.Frame = rpaframe
        self.currentData = []
        self.voltageData = []
        self.name = 'rpa'
        
    ## Everything below this is only needed for running RPA GUI without VCP ##
    def init_buttons(self):
        #method only used for running GUI independent of vcp
        #populates buttons for use without interaction with vcp
        self.Frame.btConnect.initButton(self.disconnectRPA, self.connectRPA)

        self.Frame.bttakeSweep.initButton(self.takeSweep, self.stopSweep, "Take\nSweep", "Stop\nSweep")

        self.Frame.btcalibrate.initButton(self.Frame.openCalibrateWindow, "Calibrate RPA")
        self.Frame.bteditParams.initButton(self.Frame.openConfigureWindow, "Configure Sweep\n      Parameters")
        self.Frame.btshowPlot.initButton(self.Frame.openPlotWindow, "Show IV Curve")
        self.Frame.btADCread.initButton(self.queryADC, 'Query ADC')
        self.Frame.btDACread.initButton(self.setDAC, 'Set DAC')
        self.Frame.btsaveDACpoint.initButton(lambda: self.RPA.saveDACcal(self.Frame.DACcalfilename.get(), float(self.Frame.DACvoltoutput.getData())), 'Save DAC')

    def startUpdateViewStatusLoop(self):
        self.thUpdateStatus = Thread(target = self.updateViewStatusLoop, name = 'View-Data-Update', daemon = True)
        self.thUpdateStatus.start()

    def updateViewStatusLoop(self):
        while hasattr(self, 'root'):
            self.updateViewData()
            sleep(0.1)

    def updateViewData(self):
        connectData = {}
        activeData = {}
        usedPorts = {}
        name = self.name
        
        connectData[name] = self.RPA.comStatus
        activeData[name] = self.RPA.flgActive
        if self.RPA.comStatus == 1:
            usedPorts[name] = self.RPA.comPort
        availablePorts = [port.name for port in comports() if port.name not in usedPorts.values()]
        self.data = {'current':self.RPA.current,
                     'voltage':self.RPA.voltage,
                     'temp':self.RPA.temp,
                     'density':self.RPA.density,
                     'velocity':self.RPA.velocity,
                     'adc_counts':self.RPA.adc_counts,
                     'dac_counts':self.RPA.dac_counts,
                     'current_array':self.RPA.current_array,
                     'voltage_array':self.RPA.voltage_array
                     }
        self.Frame.updateWidgets(availablePorts, connectData[name], activeData[name], self.data)

    def doTakeSweep(self):
        numsweeps = int(self.Frame.numSweeps.getData())
        dac_start = self.safe_eval(self.Frame.sweepStartVolt.getData())
        dac_end = self.safe_eval(self.Frame.sweepEndVolt.getData())
        num_steps = int(self.Frame.sweepSteps.getData())
        num_avgs = int(self.Frame.sweepAvg.getData())
        delay = int(self.Frame.sweepDelay.getData())
        mode = self.Frame.sweepMode.getData()
        
        if hasattr(self, 'RPA'):
            if self.RPA.comStatus == 1:
                cmd = self.RPA.sweep_command(dac_start, dac_end, num_steps, delay, num_avgs)
            else:
                print('RPA not connected')
                return
        else:
            print('RPA not connected')
            return

        match mode:
            case 'idle':
                print('idle mode not operational yet sorry')
            case 'rapid':
                print('rapid mode not operational yet sorry')
            case 'manual':
                print('manual sweep activated')
                for i in range(numsweeps):
                    self.RPA.sweep_num = i
                    print(f'{i}: sending sweep command {cmd}')
                    self.RPA.send_and_save_sweep(cmd, filename='')
                    print(f'sweep command {i} sent, waiting...')
                    time.sleep(0.5)
                    while self.RPA.flgActive == 1:
                        time.sleep(1)
                        
    def takeSweep(self):
        if hasattr(self, 'RPA'):
            if(self.RPA.comStatus == 1):
                self.thProgramSweep = Thread( target = self.doTakeSweep, name = self.name + '-Take-Sweep', daemon = True)
                self.thProgramSweep.start()
                return True
            else:
                print("RPA is not connected; send_and_save_sweep command not executed" )
                return False
        else:
            print('RPA not connected')
            return False


    def stopSweep(self):
        print('sorry cant stop. just gonna have to wait till its done :(')

    def setDAC(self):
        DAC_counts = self.safe_eval(self.Frame.DACcountsinput.getData())
        print(DAC_counts)
        if hasattr(self, 'RPA'):
            if self.RPA.comStatus == 1:
                cmd = self.RPA.set_dac_command(dac_volt=DAC_counts)
                print(f'sending dac command: {cmd}')
                self.RPA.setDAC(cmd)
            else:
                print('RPA not connected')
        else:
            print('RPA not connected')

    def queryADC(self):
        if hasattr(self, 'RPA'):
            num_reads = int(self.Frame.numADCreads.getData())
            if self.RPA.comStatus ==1:
                for i in range(num_reads):
                    cmd = self.RPA.poll_adc_command(255)
                    #print(f'sending adc query: {cmd}')
                    self.RPA._read_and_saveADC(cmd, float(self.Frame.ADCcurrinput.getData()), self.Frame.ADCcalfilename.getData())
            else:
                print('RPA not connected')
        else:
            print('RPA not connected')

    def connectRPA(self, ):
        print("connectRPA() method called from RPAController")
        self.RPA.connect(self.Frame.listCOM.getSelection())
        self.RPA.flgCOM = 0.5
        self.Frame.ltCOM.setYellow()

    def disconnectRPA(self):
        print( "disconnectRPA() method called from RPAController")
        self.RPA.disconnect()
        
    def safe_eval(self, text):
        text = text.strip()
        if not re.fullmatch(r'[0-9a-fx+\-*/%().<>|&^ ]+', text, re.IGNORECASE):
            raise ValueError(f'Invalid input: {text}')
        return int(eval(text))
    





class subWindow():
    def __init__(self, master, RPA_frame, windows = True):
        self.windows = windows
        self.visible = False
        if windows:
            self.window = tk.Toplevel(master)
            self.window.withdraw()

            self.window.protocol("WM_DELETE_WINDOW", self.hide)
        else:
            self.window = ttk.Frame(RPA_frame)

    def show(self):
        if self.windows:
            self.visible = True
            self.window.deiconify()
        else:
            print('Showing/Hiding additional RPA windows not available in this mode')

    def hide(self):
        if self.windows:
            self.visible = False
            self.window.withdraw()
        else:
            print('Showing/Hiding additional RPA windows not available in this mode')
        


if __name__ == "__main__":
    print("PNIFrame module test running" )
    root = tk.Tk()
    rpa = RPA()
    frame = RPAFrame( root, windows = True)
    frame.initWidgets()
    frame.pack( fill='both', expand=True )
    rpaController = RPAcontroller(root, rpa, frame)
    rpaController.init_buttons()
    rpaController.startUpdateViewStatusLoop()
    root.mainloop()