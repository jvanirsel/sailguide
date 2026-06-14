from threading import Thread
from time import sleep
import numpy as np
from collections import deque
import time
from datetime import datetime
import serial as s
import serial.tools.list_ports
from misc import ExcelManager, BreakAllLoops, FilamentTimeManager
import matplotlib.dates as md
import tkinter.filedialog as tkd
from tkinter import messagebox
from dialogWindows import calibWindow
from SlackIntegration import SlackBridge
from pathlib import Path
import re
import scipy.io as sio

class PeripheralController():
    def __init__(self, root, model, view ):
        self.root = root # for dialog windows
        self.model = model
        self.names = [ 'mc', 'l392', 'pcs', 'heat1','heat2', 'bias', 'wslp', 'pni', 'rpa']
        self.pressureData = []
        self.biasCurrentData = []
        self.biasVoltageData = []
        self.sourceTempData = []
        self.rpaVoltageData = []
        self.rpaCurrentData = []
        self.view = view
        self.log = ExcelManager()
        self.filamentLog = FilamentTimeManager()
        self.slack = SlackBridge()
        self.counter = 0
        self.counter2 = 0
        self.slackMessagesWanted = True # Decides if posting messages to slack
        
        self.StartTime = time.time()
        self.t = lambda : time.mktime(time.localtime())
        
    def bindControlNodes(self): # Initializer
        print("bindControlNodes() method called from PeripheralController class")
        
        try:
            # Bind connect buttons
            self.view.frames['mc'].btConnect.initButton( self.disconnectMC, self.connectMC )
            self.view.frames['l392'].btConnect.initButton( self.disconnectL392, self.connectL392 )
            self.view.frames['pcs'].btConnect.initButton( self.disconnectPCS, self.connectPCS )
            self.view.frames['heat1'].btConnect.initButton( self.disconnectHeat1, self.connectHeat1 )
            self.view.frames['heat2'].btConnect.initButton( self.disconnectHeat2, self.connectHeat2 )
            self.view.frames['bias'].btConnect.initButton( self.disconnectBias, self.connectBias )
            self.view.frames['wslp'].btConnect.initButton( self.disconnectWSLP, self.connectWSLP )
            self.view.frames['pni'].btConnect.initButton( self.disconnectPNI, self.connectPNI )
            self.view.frames['rpa'].btConnect.initButton( self.disconnectRPA, self.connectRPA )
            print(" bound connect buttons!")
        except Exception as e:
            print("? couldn't bind connect buttons, err ", e)
            
        try:
            # Bind 'active' buttons
            self.view.frames['mc'].btMove.initButton( self.moveMC, 'Move' )
            self.view.frames['frPC'].btIG.initButton( self.disableL392IG, self.enableL392IG, 'Disable Filaments', 'Enable Filaments' )
            self.view.frames['frPC'].btOutput.initButton( self.disablePCS, self.enablePCS, 'Cancel', 'Enable' )
            self.view.frames['heat1'].btOutput.initButton( self.disableHeat1, self.enableHeat1, 'Disable\nOutput', 'Enable\nOutput' )
            self.view.frames['heat2'].btOutput.initButton( self.disableHeat2, self.enableHeat2, 'Disable\nOutput', 'Enable\nOutput' )
            self.view.frames['bias'].btOutput.initButton( self.disableBias, self.enableBias, 'Disable\nOutput', 'Enable\nOutput' )
            self.view.frames['wslp'].btOutput.initButton( self.sweepWSLP, 'Take\nSweep' )
            self.view.frames['mc'].btAuto.initButton( self.stopAuto, self.autoSweep, 'Cancel Auto-sweep', 'Start Auto-sweep' )
            self.view.frames['mc'].btAuto.updateStatus( -1 )
            self.view.frames['pni'].btPollData.initButton( self.PNIstartPoll, self.PNIcancelPoll, 'Start Poll', 'Cancel Poll' ) # IH change
            self.view.frames['rpa'].bttakeSweep.initButton(self.RPASweep, self.RPAStopSweep, "Take Sweep", "Stop Sweep")

            print("bound active buttons!")
        except Exception as e:
            print("? couldn't bind active buttons, err ", e)
            
        try:
            # Bind extra buttons
            self.view.frames['mc'].btStop.initButton( self.stopMC, 'Stop' )
            self.view.frames['mc'].btCalibrate.initButton( self.calibrateMCDialog, 'Calibrate' )
            self.view.frames['mc'].btRepeat.initButton( self.stopRepeatedSample, self.startRepeatedSample, 'Cancel Timed Sample', 'Start Timed Sample' )
            self.view.frames['mc'].btRepeat.updateStatus( -1 )
            self.view.frames['frPC'].btSet.initButton( self.setPCS, 'Set' )
            self.view.frames['frPC'].btPlotPressure.initButton( None, self.setPlotPressure, 'Plot Pressures', 'Plot Pressures' )
            self.view.frames['frPC'].btPlotBiasVoltage.initButton( None, self.setPlotBiasVoltage, 'Plot Bias Voltage', 'Plot Bias Voltage')
            self.view.frames['frPC'].btPlotBiasCurrent.initButton( None, self.setPlotBiasCurrent, 'Plot Bias Currents', 'Plot Bias Currents')
            self.view.frames['frPC'].btPlotHeat.initButton( None, self.setPlotHeat, 'Plot Source Temp', 'Plot Source Temp')
            
            self.view.frames['heat1'].btSetInput.initButton( self.setHeat1, 'Set' )
            self.view.frames['heat2'].btSetInput.initButton( self.setHeat2, 'Set' )
            # self.view.frames['heat2'].chFollow.initButton( self.setHeat2, 'Set' )
            self.view.frames['bias'].btSetInput.initButton( self.setBias, 'Set' )
            self.view.frames['wslp'].btCancel.initButton( self.stopWSLP, 'Cancel Sweep' )
            self.view.frames['wslp'].btGenProfile.initButton( self.generateSweepProfile, 'Generate\nSweep Profile' )
            self.view.frames['wslp'].btProgramSweep.initButton( self.programSweep, 'Program\nSweep Profile' )
            self.view.frames['wslp'].btSetDir.initButton( self.setSaveDir, 'Set Save\nDirectory' )
            self.view.frames['wslp'].btUpdateFilename.initButton( self.updateFileName, 'Update\nFilename' )
            
            self.view.frames['frPlot'].btPlotSweepProfile.initButton( self.plotSweepProfile, 'Sweep\nProfile' )
            # self.view.frames['frPlot'].btPlotIV.initButton( self.plotIV, 'Plot IV\nCurves' )
            self.view.frames['frPlot'].btPlotCh1.initButton( self.plotCh1, 'Unity IV' )
            self.view.frames['frPlot'].btPlotCh2.initButton( self.plotCh2, 'High Gain IV' )
            
            self.view.frames['frPlot'].btPlotdI1.initButton( self.plotdI1, 'Unity dI/dV' )
            self.view.frames['frPlot'].btPlotdI2.initButton( self.plotdI2, 'High Gain dI/dV' )
            self.view.frames['frPlot'].btPlotEEDF.initButton( self.plotEEDF, 'EEDF' )

            self.view.frames['rpa'].btcalibrate.initButton(self.openCalibrateWindow, "Calibrate RPA")
            self.view.frames['rpa'].bteditParams.initButton(self.openConfigureWindow, "Configure Sweep")
            self.view.frames['rpa'].btshowPlot.initButton(self.openPlotWindow, "Show IV Curve")
            self.view.frames['rpa'].btADCread.initButton(self.queryRPAADC, 'Query ADC')
            self.view.frames['rpa'].btDACread.initButton(self.setRPADAC, 'Set DAC')
            self.view.frames['rpa'].btsaveDACpoint.initButton(lambda: self.model['rpa'].saveDACcal(self.view.frames['rpa'].DACcalfilename.get(), float(self.view.frames['rpa'].DACvoltoutput.getData())), 'Save DAC')
            self.view.frames['rpa'].btConfigureSweep.initButton(self.configureRPASweep, 'Configure Sweep')
            self.view.frames['rpa'].btSetSaveDir.initButton(self.setRPASaveDir, 'Set Save Directory')
            
            print("bound misc. buttons!")
        except Exception as e:
            print("? couldn't bind misc. buttons, err ", e)
            
        try:
            self.view.frames['heat1'].listRamp.bind("<<ComboboxSelected>>", self.setHeat1Ramp )
            self.view.frames['heat2'].listRamp.bind("<<ComboboxSelected>>", self.setHeat2Ramp )
            self.view.frames['bias'].listRamp.bind("<<ComboboxSelected>>", self.setBiasRamp )
            print("bound ramp time boxes!")
        except Exception as e:
            print("? couldn't bind ramptime boxes, err ", e)
            
    def startUpdateViewStatusLoop(self):
        self.thUpdateStatus = Thread( target = self.updateViewStatusLoop, name = 'View-Data-Update', daemon = True )
        self.thUpdateStatus.start()
        
    def updateViewStatusLoop(self):
        while hasattr( self.view, 'root' ):
            # print("root is ", self.view.root )
            self.updateViewData()
            sleep(0.5)
            
    def updateViewData(self):
        # print("updateViewData() method called from PeripheralController class")
        # update connection & output statuses
        connectData = {}
        activeData = {}
        usedPorts = {}
        for name in self.names:
            self.view.flgCOM[name] = self.model[name].comStatus
            connectData[name] = self.model[name].comStatus
            self.view.flgActive[name] = self.model[name].flgActive
            activeData[name] = self.model[name].flgActive
            if self.model[name].comStatus == 1:
                usedPorts[name] = self.model[name].comPort
            if self.model['pcs'].comStatus == 1 and self.model['pcs'].comPort=='COM7':
                usedPorts['MSP'] = 'COM8' # Removing the launchpad com port from the list, because it bugs me
                
        self.view.availablePorts = [port.name for port in s.tools.list_ports.comports() if port.name not in usedPorts.values()]
        
        # Transfer bias current data - Unnecessary
        # for name in self.view.frames['frSources'].names:
        #     self.model[name].biasCurrent = self.model['bias'].current
        
        
        # Save Data
        self.connectData = connectData # for filename purposes.
        # get updated data from model, sends to view for dissemination 
        self.data = {'Time':['999'],
                'Pressure':self.model['l392'].pressure, 
                'PCS setpoint':self.model['pcs'].setpoint, 
                'Motor Z':self.model['mc'].z, 
                'Motor T':self.model['mc'].t, 
                'Heat1 Setpoint':self.model['heat1'].setVoltage,
                'Heat1, V':self.model['heat1'].voltage,
                'Heat1, A':self.model['heat1'].current,
                'Heat1, T':self.model['heat1'].temperature,
                'Heat2 Setpoint':self.model['heat2'].setVoltage,
                'Heat2, V':self.model['heat2'].voltage,
                'Heat2, A':self.model['heat2'].current,
                'Heat2, T':self.model['heat2'].temperature,
                'Bias Set V':self.model['bias'].setVoltage,
                'Bias Set A':self.model['bias'].setCurrent,
                'Bias, V':self.model['bias'].voltage,
                'Bias, A':self.model['bias'].current, 
                'Bx':self.model['pni'].Bx,
                'By':self.model['pni'].By,
                'Bz':self.model['pni'].Bz,
                'RPA V':self.model['rpa'].voltage,
                'RPA I':self.model['rpa'].current,
                'RPA T':self.model['rpa'].temp,
                'RPA N':self.model['rpa'].density,
                'RPA v':self.model['rpa'].velocity,
                'RPA I_cnts':self.model['rpa'].adc_counts,
                'RPA V_cnts':self.model['rpa'].dac_counts
                }
        if self.counter == 1:
            self.log.saveData(self.data, connectData, activeData)
            self.counter2 = self.counter2+1
            if self.counter2 > 5:
                if self.slackMessagesWanted:
                    try:
                        self.slack.updateStatus(self.connectData, self.data)
                        
                    except:
                        print("error updating slack")
                if self.model['heat1'].comStatus == 1 and self.model['heat2'].comStatus==1:
                    self.filamentLog.updateFilamentUseTime( self.data['Heat1, T'], self.data['Heat2, T'] )
                self.counter2 = 0
        self.counter = self.counter^1
        
        # Transfer to View
        self.view.dvMotorPosition.update( {'z':self.model['mc'].z, 't':self.model['mc'].t} ) # [Zpos,Tpos]
        self.view.dvPressure = self.model['l392'].pressure # data['Pressure']
        self.view.dvPCSSetpoint = self.model['pcs'].setpoint 
        self.view.dvCh1 = self.model['wslp'].ch1
        self.view.dvCh2 = self.model['wslp'].ch2
        self.view.dvH = self.model['wslp'].headerData
        self.view.dvMagField = { 'Bx':self.model['pni'].Bx, 'By':self.model['pni'].By, 'Bz':self.model['pni'].Bz } # IH change
        self.view.RPAData = {'voltage':self.model['rpa'].voltage,
                'current':self.model['rpa'].current,
                'temp':self.model['rpa'].temp,
                'density':self.model['rpa'].density,
                'velocity':self.model['rpa'].velocity,
                'adc_counts':self.model['rpa'].current_counts_array,
                'dac_counts':self.model['rpa'].voltage_counts_array,
                'current_array':self.model['rpa'].current_array,
                'voltage_array':self.model['rpa'].voltage_array,
                'point_id':self.model['rpa'].pointID_array,
                'sweep_num':self.model['rpa'].sweep_num_array
                }
        self.view.RPASupportData = {'pressure':self.model['l392'].pressure,
                'Heat1, V':self.model['heat1'].voltage,
                'Heat1, A':self.model['heat1'].current,
                'Heat1, T':self.model['heat1'].temperature,
                'Heat2 Setpoint':self.model['heat2'].setVoltage,
                'Heat2, V':self.model['heat2'].voltage,
                'Heat2, A':self.model['heat2'].current,
                'Heat2, T':self.model['heat2'].temperature,
                'Bias Set V':self.model['bias'].setVoltage,
                'Bias Set A':self.model['bias'].setCurrent,
                'Bias, V':self.model['bias'].voltage,
                'Bias, A':self.model['bias'].current,
                'savefile':self.model['rpa'].getSavePath(),
                'needSave':self.model['rpa'].needSave
                }

        if self.model['wslp'].newData == 1:
            self.model['wslp'].newData = 0
            self.view.frames['wslp'].updateParameters( self.model['wslp'].headerData )
            self.model['wslp'].subtitle = self.getPlotSubtitle()
            self.view.frames['frPlot'].updatePlot( self.view.dvCh1, self.view.dvCh2, self.model['wslp'].E, self.model['wslp'].Ge,  self.model['wslp'].headerData['boardID'],self.model['wslp'].header,  self.model['wslp'].subtitle )
        for name in self.view.frames['frSources'].names:
            self.view.dvSourceV[name] = self.model[name].voltage
            self.view.dvSourceI[name] = self.model[name].current
            self.view.dvSourceSetV[name] = self.model[name].setVoltage
            if name != 'bias':
                self.view.dvSourceW[name] = self.model[name].power
                self.view.dvSourceTemp[name] = self.model[name].temperature
            else:
                self.view.dvSourceSetV[name] = [self.model[name].setVoltage, self.model[name].setCurrent ]
        
        

        # update plot data for pressure
        if self.model['l392'].comStatus == True and (self.model['l392'].pressure < 999):
            self.pressureData.append([self.t(), self.model['l392'].pressure ])
            # print("Pressure Data is ", self.pressureData)
            # print('length of data points is ', len(self.pressureData))
            try:
                if len(self.pressureData) > 120:
                    self.pressureData = self.pressureData[-120:-1]
            except IndexError:
                print("Index error(!)")
                # self.pressureData = self.pressureData[0:-1]
                # print("nada")
            except:
                print( "!!! Error converting Pressure plot points to array" )
            # print("After cropping, p data is ", self.pressureData)
            self.view.dvPressurePlot = np.asarray( self.pressureData, dtype=object )
            # print("View p data sent is ", self.view.dvPressurePlot)
        
        # Plot data for bias current
        if self.model['bias'].comStatus == True and self.model['bias'].flgActive == 1:
           self.biasCurrentData.append([self.t(), self.model['bias'].current ])
           self.biasVoltageData.append([self.t(), self.model['bias'].voltage ])
           try:
               if len(self.biasCurrentData) > 120:
                self.biasCurrentData = self.biasCurrentData[-120:-1]
                self.biasVoltageData = self.biasVoltageData[-120:-1]
           except IndexError:
               print("Index error(!)")
            #    self.biasCurrentData = self.biasCurrentData[0:-1]
            #    self.biasVoltageData = self.biasVoltageData[0:-1]
           except:
               print( "!!! Error converting Bias plot points to array" )
               
           self.view.dvBiasCurrentPlot = np.asarray( self.biasCurrentData, dtype=object )
           self.view.dvBiasVoltagePlot = np.asarray( self.biasVoltageData, dtype=object )

        
        # Plot data for source temps
        if self.model['heat1'].flgActive == 1 or self.model['heat2'].flgActive == 1:
           self.sourceTempData.append([self.t(), self.model['heat1'].temperature, self.model['heat2'].temperature, (self.model['heat1'].temperature + self.model['heat2'].temperature)/2 ])
           try:
                if len(self.sourceTempData) > 120:
                    self.sourceTempData = self.sourceTempData[-120:-1]
           except IndexError:
               print("Index error(!)")
            #    self.sourceTempData = self.sourceTempData[0:-1]
           except:
               print( "!!! Error converting Heat plot points to array" )
           self.view.dvSourceTempPlot = np.asarray( self.sourceTempData )
           
        self.model['rpa'].needSave = 0
        self.view.flgUpdate = True
    
    def startRepeatedSample(self):
        if self.view.flgCOM['wslp'] == 1:
            print("Starting Repeated WSLP Sampling: 2min period")
            self.view.repeatMode = 1
            
            ###################   Set for repeat timer period   #################
            samplePeriodMinutes = 2 # minute(s)
            self.repeatSample(samplePeriodMinutes)
        
        else:
            print("WSLP Not connected: not doing any sweeping")
            self.setScanStatus("WSLP not connected!")
            
    def doRepeatSample(self, samplePeriodMinutes):

        if self.view.repeatMode == 1 and self.view.flgCOM['wslp'] == 1 and self.view.flgActive['wslp'] != 1:
            t = datetime.now()
            # self.setScanStatus("Psuedo-sampled at "+ t.strftime("%H:%M:%S"))
            # print("Psuedo-sampled at ", t.strftime("%H:%M:%S") )
            self.view.frames['wslp'].enDataSuffix.setData("RepeatSweep-"+t.strftime("%m-%d__%H-%M-%S"))
            self.root.after( samplePeriodMinutes*60*1000, self.repeatSample, samplePeriodMinutes ) # Delay in ms: 5 min
            self.sampleWSLP()

            
    def repeatSample(self, samplePeriodMinutes):
        print("repeatSample() method called from Controller")
        self.thRepeatSample = Thread( target = self.doRepeatSample, name = 'Repeat-Sample', daemon = True, args = (samplePeriodMinutes, ) )
        self.thRepeatSample.start()
    
    def stopRepeatedSample(self):
        self.view.repeatMode = -1
        self.setScanStatus("Repeated Sample stopped")
        print("stopRepeatedSample() method called from controller")
        
    
    def autoSweep(self):
        print("autoSweep() method called from Controller")
        self.thAutoSweep = Thread( target = self.doAutoSweep, name = 'Auto-Sweep', daemon = True )
        self.thAutoSweep.start()
        
    
    def stopAuto(self):
        print("stopAuto() method called. Setting autoMode to False (-1)")
        self.view.autoMode = -1
        
    
    def doAutoSweep(self):
        params = self.view.frames['mc'].getParameters(self.data)
        # status = self.view.frames['auto'].enStatus
        # print(params)

        if params:
            try:
                print("\n\nStarting autosweep\n\n")
                self.view.autoMode = 1
                progressTotal = len(params['Z'])*len(params['T'])
                print("Number of stops: ", progressTotal )
                count = 0
                for z in params['Z']:
                    if self.view.autoMode == -1:
                        raise BreakAllLoops
                    print("      Setting Z distance to ", z)
                    self.view.frames['mc'].dvAutoProgress.set(count/progressTotal * 100)
                    self.setScanStatus("Moving to Z="+'{:.0f}'.format(z)+"cm")
                    self.view.frames['mc'].enInputZ.setData( z )
                    self.model['mc'].move( '{:.1f}'.format(z), '' )
                    self.waitForStop( 60 ) 
                        
                    self.setScanStatus("Making small position adjustments")
                    sleep(2)
                    # Let it adjust as necessary in case of small overshoot
                    self.model['mc'].move( '{:.1f}'.format(z), '' )
                    sleep(2)
                    self.waitForStop( 30 )
                    
                    self.setScanStatus("Letting chamber settle...")
                    numPoints = 10 # 60/2 = 30 seconds settle time
                    for i in range(numPoints):
                        sleep(0.5)
                        self.view.frames['mc'].dvAutoProgress.set((i+1) * 100/numPoints)
                        if self.view.autoMode == -1:
                            raise BreakAllLoops

                    # if count == 0:
                        # self.waitForStop( 480 )
                    # else:
                        # self.waitForStop( 120 )
                        
                    for theta in params['T']:
                        if self.view.autoMode == -1:
                            raise BreakAllLoops
                        print("         Setting angle to ", theta )#, "\n     sweep!")
                        self.setScanStatus("Moving to T="+'{:.1f}'.format(theta)+"°")
                        self.view.frames['mc'].dvAutoProgress.set(count/progressTotal * 100)
                        self.view.frames['mc'].enInputT.setData( theta )
                        self.view.frames['mc'].enInputZ.setData( '' )
                        self.model['mc'].move( self.view.frames['mc'].enInputZ.getData(), '{:.1f}'.format(theta) )
                        sleep(8)
                        self.waitForStop( 2*15*(abs(theta - int(self.model['mc'].t)))+90 )    
                
                        
                        count = count+1
                        
                        
                        # sleep(1)
                        # self.model['mc'].move( '', '{:.1f}'.format(theta) )
                        # sleep(1)
                        # self.waitForStop( 90 )

                        if self.view.autoMode == -1:
                            print("Automode disabled")
                            raise BreakAllLoops
                        
                        # smaple
                        #self.sampleWSLP()
                        
                    params['T'] = np.flip(params['T'])
                    
            except BreakAllLoops:
                print("Automode disabled. Exiting auto scan loop...")
                self.slack.sendMessageToJonas("Aborted scan loop")
            except Exception as err:
                print("Unexpected error in autosweep, ", err)
                
        if self.view.autoMode == -1:
            self.stopMC()
            self.setScanStatus("Motor Scan Loop aborted.")
            self.view.frames['mc'].dvAutoProgress.set(0)
            print("Aborted")
        else: 
            print("finished loop")
            self.slack.sendMessageToJonas("Scan loop complete! :bean:")
            self.setScanStatus("Motor Scan Loop complete.")
            self.view.autoMode = -1
        # if self.view.frames['auto'].getParameters(self.data):
        #     self.view.autoMode = 1
        #     counter = 0
        #     countMultiplier = 10
        #     flgBreak = False
            # sleep(3)
            
            # while counter*countMultiplier <= 100 and self.view.autoMode == 1:
            #     sleep(0.5)
            #     if self.view.autoMode == -1:
            #         flgBreak = True
            #         break
            #     self.view.frames['auto'].dvAutoProgress.set(counter*countMultiplier)
            #     counter = counter + 1
            #     print("counter is at ", counter)
            
    def sampleWSLP(self):
        self.setScanStatus("Sweeping WSLP...")
        self.updateFileName()
        t = datetime.now()
        if self.model['wslp'].doTakeSweep(True, self.data):
            self.setScanStatus("Last sweep: " + t.strftime("%H:%M:%S") )
        else:
            self.setScanStatus("Error; re-trying...")
            if self.model['wslp'].validateConnection():
                self.model['wslp'].doTakeSweep(True, self.data)
            else:
                self.setScanStatus('WSLP Connection Error')
                self.view.repeatMode = -1
                self.view.autoMode = -1
        
    def waitForStop(self, maxWait):
        counter = 1
        while self.view.autoMode == 1 and self.model['mc'].isMoving():
            sleep(1)
            counter = counter + 1
            if counter > maxWait:
                print("!!!    wait time has exceeded ", maxWait, " seconds, aborting...")
                print("       Motor condition: z=", self.model['mc'].z, ", t=", self.model['mc'].t )
                self.view.autoMode = -1
                return
        print("Setpoint reached!")
        
    def _kill_all(self):
        for name in self.names:
            self.model[name].disconnect()

# Callbacks
    def callback(self, eventObject): # Test
        print("yeeeehaw!!")

    # Connect/disconnect
    def connectMC(self):
        print( "connectMC() method called from PeripheralController")
        self.model['mc'].connect( self.view.frames['mc'].listCOM.getSelection() )
        self.model['mc'].flgCOM = 0.5
        self.view.frames['mc'].ltCOM.setYellow()
        
    def disconnectMC(self):
        print( "disconnectMC() method called from PeripheralController")
        self.model['mc'].disconnect()
        
    def connectL392(self):
        print( "connectL392() method called from PeripheralController")
        self.model['l392'].connect( self.view.frames['l392'].listCOM.getSelection() )
        self.model['l392'].flgCOM = 0.5
        self.view.frames['l392'].ltCOM.setYellow()
        
    def disconnectL392(self):
        print( "disconnectL392() method called from PeripheralController")
        self.model['l392'].disconnect()
    
    def connectPCS(self):
        print( "connectPCS() method called from PeripheralController")
        self.model['pcs'].connect( self.view.frames['pcs'].listCOM.getSelection() )
        self.model['pcs'].flgCOM = 0.5
        self.view.frames['pcs'].ltCOM.setYellow()
        
    def disconnectPCS(self):
        print( "disconnectPCS() method called from PeripheralController")
        self.model['pcs'].disconnect()
        
    def connectHeat1(self):
        print( "connectHeat1() method called from PeripheralController")
        self.model['heat1'].connect( self.view.frames['heat1'].listCOM.getSelection() )
        self.model['heat1'].flgCOM = 0.5
        self.view.frames['heat1'].ltCOM.setYellow()
        
    def disconnectHeat1(self):
        print( "disconnectHeat1() method called from PeripheralController")
        self.model['heat1'].disconnect()
        
    def connectHeat2(self):
        print( "connectHeat2() method called from PeripheralController")
        self.model['heat2'].connect( self.view.frames['heat2'].listCOM.getSelection() )
        self.model['heat2'].flgCOM = 0.5
        self.view.frames['heat2'].ltCOM.setYellow()
        
    def disconnectHeat2(self):
        print( "disconnectHeat2() method called from PeripheralController")
        self.model['heat2'].disconnect()
        
    def connectBias(self):
        print( "connectBias() method called from PeripheralController")
        self.model['bias'].connect( self.view.frames['bias'].listCOM.getSelection() )
        self.model['bias'].flgCOM = 0.5
        self.view.frames['bias'].ltCOM.setYellow()
        
    def disconnectBias(self):
        print( "disconnectBias() method called from PeripheralController")
        self.model['bias'].disconnect()
        
    def connectWSLP(self):
        print( "connectWSLP() method called from PeripheralController")
        self.model['wslp'].connect( self.view.frames['wslp'].listCOM.getSelection() )
        self.model['wslp'].flgCOM = 0.5
        self.view.frames['wslp'].ltCOM.setYellow()
        
    def disconnectWSLP(self):
        print( "disconnectWSLP() method called from PeripheralController")
        self.model['wslp'].disconnect()
        
    def connectPNI(self):
        print( "connectPNI() method called from PeripheralController")
        self.model['pni'].connect( self.view.frames['pni'].listCOM.getSelection() )
        self.model['pni'].flgCOM = 0.5
        self.view.frames['pni'].ltCOM.setYellow()
        
    def disconnectPNI(self):
        print( "disconnectPNI() method called from PeripheralController")
        self.model['pni'].disconnect()

    #RPA
    def connectRPA(self):
        print( "connectRPA() method called from PeripheralController")
        self.model['rpa'].connect( self.view.frames['rpa'].listCOM.getSelection() )
        self.model['rpa'].flgCOM = 0.5
        self.view.frames['rpa'].ltCOM.setYellow()
        
    def disconnectRPA(self):
        print( "disconnectRPA() method called from PeripheralController")
        self.model['rpa'].disconnect()

            # self.view.frames['rpa'].btADCread.initButton(self.queryADC, 'Query ADC')
            # self.view.frames['rpa'].btDACread.initButton(self.setDAC, 'Set DAC')
            # self.view.frames['rpa'].btsaveDACpoint.initButton(lambda: self.RPA.saveDACcal(self.Frame.DACcalfilename.get(), float(self.Frame.DACvoltoutput.getData())), 'Save DAC')
        
    def openCalibrateWindow(self):
        print('openCalibrateWindow called from PeripheralController')
        self.view.frames['rpa'].openCalibrateWindow()
    
    def openPlotWindow(self):
        print('openPlotWindow called from PeripheralController')
        self.view.frames['rpa'].openPlotWindow()

    def openConfigureWindow(self):
        print('openConfigureWindow called from PeripheralController')
        self.view.frames['rpa'].openConfigureWindow()

    def queryRPAADC(self):
        print("setRPAADC() method called from Controller")
        self.thSetADC = Thread( target = self.doSetADC, name = 'set-RPA-ADC', daemon = True )
        self.thSetADC.start()

    def setRPADAC(self):
        print("setRPADAC() method called from Controller")
        self.thSetDAC = Thread( target = self.doSetDAC, name = 'set-RPA-DAC', daemon = True )
        self.thSetDAC.start()
    
    def doSetDAC(self):
        pass

    def RPASweep(self):
        print("RPASweep() method called from Controller")
        self.thRPASweep = Thread( target = self.doRPASweep, name = 'RPA-Sweep', daemon = True )
        self.thRPASweep.start()
    
    def doRPASweep(self):
        mode = self.view.frames['rpa'].sweepMode.getData()
        numsweeps = int(self.view.frames['rpa'].numSweeps.getData())
        cmd = self.model['rpa'].cmd
        filename=self.view.frames['rpa'].sweepFileName.getData()
        
        match mode:
            case 'idle':
                print('idle mode not operational yet sorry')
            case 'rapid':
                print('rapid mode not operational yet sorry')
            case 'manual':
                print('manual sweep activated')
                for i in range(numsweeps):
                    self.model['rpa'].sweep_num += 1
                    print(f'{i}: sending sweep command {cmd}')
                    self.model['rpa'].send_and_save_sweep(cmd, filename=self.view.frames['rpa'].sweepFileName.getData())
                    print(f'sweep command {i} sent, waiting...')
                    time.sleep(0.1)
                    while self.model['rpa'].flgActive == 1:
                        time.sleep(1)

    def RPAStopSweep(self):
        pass
        
    def configureRPASweep(self):
        print("configureRPASweep() method called from Controller")
        dac_start = self.safe_eval(self.view.frames['rpa'].sweepStartVolt.getData())
        dac_end = self.safe_eval(self.view.frames['rpa'].sweepEndVolt.getData())
        num_steps = int(self.view.frames['rpa'].sweepSteps.getData())
        num_avgs = int(self.view.frames['rpa'].sweepAvg.getData())
        delay = int(self.view.frames['rpa'].sweepDelay.getData())
        
        t = "{:%Y_%m_%d}".format(datetime.now())
        

        if self.model['rpa'].comStatus == 1:
            self.model['rpa'].cmd = self.model['rpa'].sweep_command(dac_start, dac_end, num_steps, delay, num_avgs)
            filename = t+f"_{int(self.model['rpa'].cnts2volt(dac_start))}_{int(self.model['rpa'].cnts2volt(dac_end))}_{num_steps}.mat"
            self.view.frames['rpa'].sweepFileName.setData(filename)
            full_filepath = Path(self.model['rpa'].filepath/datetime.now().strftime('%m-%d-%y')/filename)
            #print(str(full_filepath))
            i = 0
            while full_filepath.exists():
                print('filealready exists')
                num = f'({i})'
                full_filepath = full_filepath/num
                #self.model['rpa'].sweepFileName.setData(filename/num)
        else:
            print('RPA not connected')
            return
            
    def setRPASaveDir(self):
        print( 'setRPASaveDir() method called from PeripheralController' )
        dataDirectory = tkd.askdirectory()
        if dataDirectory == '':
            print("No new directory selected.")
            print("Current Directory is ", self.model['rpa'].filepath)
        else:
            print("New Data Directory is ", dataDirectory)
            self.model['rpa'].filepath = Path(dataDirectory)

    # Enable/Disable
    def moveMC(self):
        print( "moveMC() method called from PeripheralController" )
        in_z = self.view.frames['mc'].enInputZ.getData()
        in_t = self.view.frames['mc'].enInputT.getData()
        self.model['mc'].move( in_z, in_t )
        self.model['mc'].flgActive = 0.5
        self.view.frames['mc'].ltActive.setYellow()
        
    def enableL392IG(self):
        print( "enableL392IG() method called from PeripheralController" )
        self.model['l392'].flgActive = 0.5
        self.view.frames['l392'].ltActive.setYellow()
        self.model['l392'].enableIG()
    
    def disableL392IG(self):
        print( "disableL392IG() method called from PeripheralController" )
        self.model['l392'].disableIG()
        
    def enablePCS(self):
        print( 'enablePCS() method called from PeripheralController' )
        self.model['pcs'].flgActive = 0.5
        self.view.frames['pcs'].ltActive.setYellow()
        self.model['pcs'].enableControl()
        
    def disablePCS(self):
        print( 'disablePCS() method called from PeripheralController' )
        self.model['pcs'].disableControl()
        
    def enableHeat1(self):
        print( 'enableHeat1() method called from PeripheralController' )
        self.model['heat1'].flgActive = 0.5
        self.view.frames['heat1'].ltActive.setYellow()
        self.setHeat1Ramp( self.view.frames['heat1'].listRamp.getSelection() )
        self.model['heat1'].enableOutput()
        
    def disableHeat1(self):
        print( 'disableHeat1() method called from PeripheralController' )
        self.model['heat1'].disableOutput()
        
    def enableHeat2(self):
        print( 'enableHeat2() method called from PeripheralController' )
        self.model['heat2'].flgActive = 0.5
        self.view.frames['heat2'].ltActive.setYellow()
        self.setHeat2Ramp( self.view.frames['heat2'].listRamp.getSelection() )
        self.model['heat2'].enableOutput()
        
    def disableHeat2(self):
        print( 'disableHeat2() method called from PeripheralController' )
        self.model['heat2'].disableOutput()
        
    def enableBias(self):
        print( 'enableBias() method called from PeripheralController' )
        self.model['bias'].flgActive = 0.5
        self.view.frames['bias'].ltActive.setYellow()
        self.setBiasRamp( self.view.frames['bias'].listRamp.getSelection() )
        self.model['bias'].enableOutput()
        
    def disableBias(self):
        print( 'disableBias() method called from PeripheralController' )
        self.model['bias'].disableOutput()
        
    def sweepWSLP(self):
        # TODO: nothing, just wanted the IDE flag here
        print( 'sweepWSLP() method called from PeripheralController' )
        if self.model['wslp'].validateConnection():
            self.model['wslp'].flgActive = 1
            self.view.frames['wslp'].ltActive.setGreen()
            self.updateFileName()
            self.model['wslp'].subtitle = self.getPlotSubtitle()
            self.model['wslp'].takeSweep( self.view.frames['wslp'].vSaveMe.get(), self.data )
        else:
            self.disconnectWSLP()
            
        # Other buttons
    def stopMC(self):
        print( 'stopMC() method called from PeripheralController' )
        self.model['mc'].stop()
        
    def calibrateMCDialog(self):
        print("calibrateMC() method called")
        if not hasattr(self, 'window'):
            self.window = calibWindow(self.root, self.calibrateMC)
        else:
            print("Window already exists")
        # self.window.b['command'] = self.calibrateMC
        
    def calibrateMC(self): # To be replaced soon
        # print("Grabbing motor values...")
        try:
            self.window.destroy()
            del self.window
            self.model['mc'].calibrate()
        except:
            pass
        # if self.model['mc'].comStatus == 1:
        #     self.model['mc'].offsetZ = self.model['mc'].z - 100
        #     self.model['mc'].offsetT = self.model['mc'].t
        #     print( "Offsets are ",self.model['mc'].offsetZ, "cm z and ", self.model['mc'].offsetT, "° T" )
        
        
        
        
    def setPCS(self):
        print( 'setPCS() method called from PeripheralController' )
        setPressure = self.view.frames['frPC'].enInput.getData()
        self.model['pcs'].txSetpoint( setPressure )
        
    def setPlotPressure(self):
        print( 'setPlotPressure() method called from peripheral controller')
        self.view.plotVal = 'pressure'
    
    def setPlotBiasVoltage(self):
        print( 'setPlotBiasVoltage() method called from peripheral controller' )
        self.view.plotVal = 'biasV'
    
    def setPlotBiasCurrent(self):
        print( 'setPlotBiasCurrent() method called from peripheral controller' )
        self.view.plotVal = 'biasI'
        
    def setPlotHeat(self):
        print( 'setPlotHeat() method called from peripheral controller' )
        self.view.plotVal = 'heat'
        
        
    def setHeat1(self):
        print( 'setHeat1() method called from PeripheralController' )
        setVoltage = self.view.frames['heat1'].enInput.getData()
        self.model['heat1'].setOutput( setVoltage, None )
        
    def setHeat2(self):
        print( 'setHeat2() method called from PeripheralController' )
        
        setVoltage = self.view.frames['heat2'].enInput.getData()
        self.model['heat2'].setOutput( setVoltage, None )
        
    def setBias(self):
        print( 'setBias() method called from PeripheralController' )
        setVoltage = self.view.frames['bias'].enInputV.getData()
        setCurrent = self.view.frames['bias'].enInputI.getData()
        self.model['bias'].setOutput( setVoltage, setCurrent )
        
    def setHeat1Ramp(self, eventObject):
        print( 'setHeat1Ramp() method called from PeripheralController' )
        rampTime = self.view.frames['heat1'].listRamp.getSelection()
        self.model['heat1'].setRamp( rampTime )
        # if self.frame[]
        
    def setHeat2Ramp(self, eventObject):
        print( 'setHeat2Ramp() method called from PeripheralController' )
        rampTime = self.view.frames['heat2'].listRamp.getSelection()
        self.model['heat2'].setRamp( rampTime )
        
    def setBiasRamp(self, eventObject):
        print( 'setBiasRamp() method called from PeripheralController' )
        rampTime = self.view.frames['bias'].listRamp.getSelection()
        self.model['bias'].setRamp( rampTime )
        
    # add other WSLP methods here as needed
    def stopWSLP(self):
        print( 'stopWSLP() method called from PeripheralController' )
        print( 'stopWSLP() method is not defined!')
        
    def generateSweepProfile(self):
        # print( 'generateSweepProfile() method called from PeripheralController' )
        numSteps = int(self.view.frames['wslp'].enNumSteps.getData())
        numSweeps = int(self.view.frames['wslp'].enNumSweeps.getData())
        numDwells = int(self.view.frames['wslp'].enNumDwells.getData())
        numGroups = int(self.view.frames['wslp'].enNumGroups.getData())
        numSamples = int(self.view.frames['wslp'].enNumSamples.getData())
        if not (numSteps =='' or numSweeps=='' or numDwells=='' or numSamples=='' ):
            self.model['wslp'].dwellSide = self.view.frames['wslp'].listDwellSide.get()
            self.model['wslp'].generateSweepProfile( numSweeps, numSteps, numDwells, numGroups )
        
    def programSweep(self):
        print( 'programSweep() method called from PeripheralController' )
        numSteps = self.view.frames['wslp'].enNumSteps.getData()
        numSweeps = self.view.frames['wslp'].enNumSweeps.getData()
        numDwells = self.view.frames['wslp'].enNumDwells.getData()
        numSamples = self.view.frames['wslp'].enNumSamples.getData()
        if not (numSteps =='' or numSweeps=='' or numDwells=='' or numSamples=='' ):
            self.model['wslp'].dwellSide = self.view.frames['wslp'].listDwellSide.get()
            self.model['wslp'].programSweep( int(numSweeps), int(numSteps), int(numDwells), int(numSamples))
        
    def setSaveDir(self):
        print( 'setSaveDir() method called from PeripheralController' )
        dataDirectory = tkd.askdirectory()
        if dataDirectory == '':
            print("No new directory selected.")
            print("Current Directory is ", self.model['wslp'].filepath)
        else:
            print("New Data Directory is ", dataDirectory)
            self.model['wslp'].filepath = dataDirectory

    def updateFileName(self):
        print("updateFileName() method called from Controller")
        prefix = self.view.frames['wslp'].enDataPrefix.getData()
        suffix = self.view.frames['wslp'].enDataSuffix.getData()
        self.model['wslp'].setFileName( prefix, suffix, self.data, self.connectData )
        self.view.frames['wslp'].enFileName.setData( self.model['wslp'].filename )

    def setScanStatus(self, displayData):
        self.view.frames['mc'].enStatus.setData(displayData)


    # Plot Frame methods
    def plotSweepProfile(self):
        print("plotSweepProfile() method called from PeripheralController" )
        # if not self.model['wslp'].sweepProfile.any():
        self.generateSweepProfile()
        self.view.frames['frPlot'].plotSweepProfile( self.model['wslp'].sweepProfile )
        
    def getPlotSubtitle(self):
        # print("getPlotSubtitle() method called from controller")
        # print( "Prefix is ", prefix, ", suffix is ", suffix)
        # print("data is ", data)
        filename = ''
        # Assemble filename in the following order:
        # [prefix]__[pressure]Torr_[Vbias]V-[Ibias]bias_[Avg temp]_[Z]z_[±T]t__[suffix]
        # If a peripheral is unconnected, then skip that section
        try:
            # if prefix != '':
            #     filename = filename + prefix + '__'
            if self.connectData['l392'] == 1:
                p = '{:.2e}'.format(self.data['Pressure'])
                filename = filename + p[0:-2]+p[-1]+' Torr; '
                
            if self.connectData['bias'] == 1:
                a = '{:.1f}'.format(self.data['Bias, A'])
                filename = filename + '{:.0f}V'.format(self.data['Bias, V']) + ', ' + a[0:-2]+'.' +a[-1]+'A Bias; '
                
            if self.connectData['heat1'] == 1 or self.connectData['heat2'] == 1:
                if self.connectData['heat1'] == 1 and self.connectData['heat2'] == 0:
                    temp = self.data['Heat1, T']
                if self.connectData['heat2'] == 0 and self.connectData['heat2'] == 1:
                    temp = self.data['Heat1, T']
                if self.connectData['heat1'] == 1 and self.connectData['heat2'] == 1:
                    temp = (self.data['Heat1, T']+self.data['Heat2, T'])/2
                filename = filename + '{:.0f}K Heat; '.format(temp)
                
            if self.connectData['mc'] == 1:
                z = '{:.0f}cm Z'.format(self.data['Motor Z'])
                t = ', {:.1f}° T'.format(self.data['Motor T'])
                filename = filename + z + t
                # print("subtitle is ", filename)
            # if suffix != '':
            #     filename = filename + '__' + suffix
            
            # print("Subtitle is ", filename)
        except TypeError:
            print("Something was the wrong type for ")
        except:
            print("Error setting filename")
            return 'error'
        return filename
    
    def updateJonas(self, updateText):
        self.slack.sendMessageToJonas(updateText)
            
    # Need to flesh out these guys for different WSLPs
    def plotIV(self): # Depreciated
        print("plotIV() method called from PeripheralController")
        if self.model['wslp'].ch1.any():
            self.view.frames['frPlot'].plotCh1( self.model['wslp'].ch1 )
            
    # ch, chNum, sweepNum, boardID, header, subtitle
    def plotCh1(self):
        print("plotCh1() method called from PeripheralController")
        if self.model['wslp'].ch1.any():
            self.view.frames['frPlot'].plotSingleIV( self.model['wslp'].ch1, 1, self.view.frames['frPlot'].listSweepNum.getSelection(), self.model['wslp'].h['boardID'], self.model['wslp'].header, self.model['wslp'].subtitle )
            
    def plotCh2(self):
        print("plotCh2() method called from PeripheralController")
        if self.model['wslp'].ch2.any():
            self.view.frames['frPlot'].plotSingleIV( self.model['wslp'].ch2, 2, self.view.frames['frPlot'].listSweepNum.getSelection(), self.model['wslp'].h['boardID'], self.model['wslp'].header,  self.model['wslp'].subtitle )
            
    def plotdI1(self):
        print("plotdI1() method called from PeripheralController")
        if self.model['wslp'].ch1.any():
            self.view.frames['frPlot'].plotSingledIdV( self.model['wslp'].ch1, 1, self.view.frames['frPlot'].listSweepNum.getSelection(), self.model['wslp'].h['boardID'], self.model['wslp'].header, self.model['wslp'].subtitle )
            
    def plotdI2(self):
        print("plotCh2() method called from PeripheralController")
        if self.model['wslp'].ch2.any():
            self.view.frames['frPlot'].plotSingledIdV( self.model['wslp'].ch2, 2, self.view.frames['frPlot'].listSweepNum.getSelection(), self.model['wslp'].h['boardID'], self.model['wslp'].header, self.model['wslp'].subtitle )

    def plotEEDF(self):
        print("plotEEDF() method called from Controller")
        if self.model['wslp'].ch1.any():
            self.view.frames['frPlot'].plotEEDF(self.model['wslp'].E, self.model['wslp'].Ge, self.view.frames['frPlot'].listSweepNum.getSelection(), self.model['wslp'].subtitle)

    def PNIstartPoll(self):
        print("PNIstartPoll() method called")
        self.model['pni'].PNIpoll()
    
    def PNIcancelPoll(self):
        print("PNIcancelPoll() method called")
        print("Unbound/unfinished/maybe its not supposed to do anything anyway")
        
    def safe_eval(self, text):
        text = text.strip()
        if not re.fullmatch(r'[0-9a-fx+\-*/%().<>|&^ ]+', text, re.IGNORECASE):
            raise ValueError(f'Invalid input: {text}')
        return int(eval(text))
       
        
        # From init
        # self.t = lambda : (time.time() - self.StartTime)
        # self.startupLogtime = datetime.datetime.now()
        # self.Logt = lambda : datetime.datetime.now().strftime("%I:%M:%S%p, %B %d %Y ")
        # self.timestamp = lambda : datetime.datetime.now().strftime("%I:%M:%S%p - ")
        # self.Logstart = self.startupLogtime.strftime("%d_%B_%Y__%I_%M%p")

# for testing things
# from PressureControlSystem import PressureController
# from Lesker import Lesker392
# from MotorController import MotorController
# from BKPrecision import BKP9115
# from SLP import WSLP
# import tkinter as tk


# model = [ None, None, None, None, None, None, None ]
# model[0] = MotorController()
# model[1] = Lesker392()
# model[2] = PressureController( model[1] )
# model[3:5] = [ BKP9115('Heat #1'), BKP9115('Heat #2') ]
# model[5] = BKP9115('Bias')
# model[6] = WSLP()

# c = PeripheralController( model, tk.Frame )
# print("Lesker/pcs IG Names are: ")
# print( c.l392.name )
# print( c.pcs.pressureGauge.name )

# c.l392.setName("George")
# print("Now they are ")
# print( c.l392.name )
# print( c.pcs.pressureGauge.name )

# test 2
# print("MOdel/l392 IG Names are: ")
# print( c.model[1].name )
# print( c.l392.name )

# c.l392.setName("George")
# print("Now they are ")
# print( c.model[1].name )
# print( c.l392.name )