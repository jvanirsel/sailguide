import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as md
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from VCP_GUI_Elements import * 

class PressureControllerFrame( ttk.Frame ):
    #Constructor
    def __init__(self, parent): #, listL392, listPCS, btL392Connect, btPCSConnect,\
                 #btIG, btOutput, btSet, ltL392COM, ltPCSCOM, ltIG, ltActive, enInput ):
        self.name = 'PCS'
        super().__init__(parent)

        # try:
        #     self.grid_propagate(0)
        #     self['width'] = round((1800-400)/2)
        #     self['height'] = round(1000/2)
        # except:
        #     print("don't like me")
        
        self['borderwidth'] = 1
        self['relief'] = 'solid'
        self['padding'] = ('0.1c', '0.1c')

        
        # self.initWidgets()

    def initWidgets(self): # calls all subsequent methods
        self.frCOM = ttk.Frame( self )
        self.frData = ttk.Frame( self )
        self.frPlot = ttk.Frame( self )
        
        
        self.frL392 = LeskerCOMFrame( self.frCOM )
        self.frPCS = PCSCOMFrame( self.frCOM )
        self.frL392.initWidgets()
        self.frPCS.initWidgets()
        
        # self.listL392 = PortSelectorBox( self.frCOM, 'l392' )
        # self.listPCS = PortSelectorBox( self.frCOM, 'pcs' )
        # self.btL392Connect = ConnectButton( self.frCOM, 'l392connect' )
        # self.btPCSConnect = ConnectButton( self.frCOM, 'l392connect' )
        # self.ltL392COM = StatusLight( self.frCOM, 'l392COM' )
        # self.ltPCSCOM = StatusLight( self.frCOM, 'pcsCOM' )
        # self.ltIG = StatusLight( self.frCOM, 'l392ig' )
        # self.ltActive = StatusLight( self.frCOM, 'pcs' )
        
        self.btIG = PushButton( self.frData, 'ig' )
        self.btOutput = PushButton( self.frData, 'PCSOutput' )
        self.btSet = ClickButton( self.frData, 'pcsset' )
        self.enInput = DataEntry( self.frData, 'pcsInSet', True, 8 )
        self.enPressure = DataEntry(self.frData, 'PressureData', False, 8 )
        self.enSetpoint = DataEntry(self.frData, 'PCSInput', False, 8 )
        
        self.btPlotPressure = PushButton( self.frPlot, 'Pressures' )
        self.btPlotBiasVoltage = PushButton( self.frPlot, 'Bias Volts')
        self.btPlotBiasCurrent = PushButton( self.frPlot, 'Bias Currents')
        self.btPlotHeat = PushButton( self.frPlot, 'Heat')
        
        
        
        self.initLabels()
        self.initLocations()
        self.initPlotFrame()
        
        
    def initLabels(self):
        self.lblTitle = ttk.Label( self, text = 'Pressure Controller', style = 'Header.TLabel')
        
        self.lblPressure = ttk.Label( self.frData, text = 'Pressure:', style = 'Std.TLabel')
        self.lblUnit1 = ttk.Label( self.frData, text = 'Torr', style = 'Std.TLabel')
        self.lblSetpoint = ttk.Label( self.frData, text = 'Pressure Setpoint:', style = 'Std.TLabel')
        self.lblInputSet = ttk.Label( self.frData, text = 'Input Set Pressure:', style = 'Std.TLabel')
        self.lblUnit2 = ttk.Label( self.frData, text = 'Torr', style = 'Std.TLabel')
        self.lblUnit3 = ttk.Label( self.frData, text = 'Torr', style = 'Std.TLabel')
        
    
    def initLocations(self):
        self.lblTitle.grid( row = 0, column = 0 )#, sticky = 'nesw' )
        
        self.columnconfigure( index=1, weight=0 )
        self.rowconfigure( index=0, weight=1 )
        self.rowconfigure( index=1, weight=2)
        self.rowconfigure( index=2, weight=3)
        self.rowconfigure( index=3, weight=20)
        

        self.frCOM.columnconfigure(index=0, weight=0)
        self.frCOM.columnconfigure(index=1, weight=1)
        self.frCOM.columnconfigure(index=2, weight=0)
        self.frCOM.rowconfigure(index=0, weight=1)
        # self.frCOM['relief'] = 'raised'
        self.frCOM['padding'] = ('0.25c', '0.15c')
        self.frCOM.grid( row = 1, column = 0, sticky = 'ns' )
        self.frL392.grid( row = 0, column = 0, sticky = 'nsew' )
        self.frPCS.grid( row = 0, column = 2, sticky = 'ns' )
        
        
        self.frData.columnconfigure(index=4, weight=1)
        self.frData.rowconfigure(index=0, weight=1)
        self.frData['padding'] = ('0.25c', '0.15c')
        self.frData.grid( row = 2, column = 0, columnspan = 3, sticky = 'nsew' )
        self.lblPressure.grid( row = 0, column = 0 )
        self.enPressure.grid( row = 0, column = 1 )
        self.lblUnit1.grid( row = 0, column = 2, sticky = 'w' )
        self.lblInputSet.grid( row = 0, column = 4, sticky = 'e' )
        self.enInput.grid( row = 0, column = 5 )
        self.lblUnit2.grid( row = 0, column = 6, sticky = 'w' )
        self.btSet.grid( row = 0, column = 7 )
        self.btIG.grid( row = 1, column = 0, columnspan = 3 )
        self.lblSetpoint.grid( row = 1, column = 4, sticky = 'e' )
        self.enSetpoint.grid( row = 1, column = 5 )
        self.lblUnit3.grid( row = 1, column = 6, sticky = 'w' )
        self.btOutput.grid( row = 1, column = 7 )
        
        self.frPlot.grid( row = 3, column = 0)#, sticky = 'nsew' )
        self.frPlot['relief'] = 'sunken'
        self.btPlotPressure.grid( row = 0, column = 0, sticky = 'e')
        self.btPlotBiasVoltage.grid( row = 0, column = 1, sticky = 'ew')
        self.btPlotBiasCurrent.grid( row = 0, column = 2, sticky = 'ew')
        self.btPlotHeat.grid( row = 0, column = 3, sticky = 'w')
        
    
    def updateWidgets(self, ports, portL392Status, portPCSStatus, igStatus, outputStatus, pressure, setpoint, plotPressureData, plotBiasVData, plotBiasIData, plotHeatData, plotVal, autoMode):
        # print("updateWidgets() method called from PressureControllerFrame")
        
        # print("Port output statuses: Lesker - ", igStatus, "; PCS - ", outputStatus)
        
        self.frL392.ltCOM.updateStatus( portL392Status )
        self.frL392.listCOM.updateStatus( portL392Status, ports )
        self.frPCS.ltCOM.updateStatus( portPCSStatus )
        self.frPCS.listCOM.updateStatus( portPCSStatus, ports )
        self.frL392.btConnect.updateStatus( portL392Status )
        self.frPCS.btConnect.updateStatus( portPCSStatus )
        
        
        if autoMode == 1: # If AutoMode
            # print("updateWidget() method called in Auto Mode from Pressure Controller frame")
            self.frPCS.ltActive.updateStatus( outputStatus )
            self.enSetpoint.setData( '{:.2e}'.format(setpoint) )
            self.btSet.updateStatus( 0 )
            self.btOutput.updateStatus( 0 )
            self.btIG.updateStatus( igStatus )#^ True )
            self.frL392.ltActive.updateStatus( igStatus ^ True )
            self.enPressure.setData( '{:.2e}'.format(pressure) )
        else: # If normal operations
            if portL392Status == 1:
                self.btIG.updateStatus( igStatus ^ True )
                self.frL392.ltActive.updateStatus( igStatus ^ True )
                self.enPressure.setData( '{:.2e}'.format(pressure) )
            else:
                self.btIG.updateStatus( 0 )
                self.frL392.ltActive.updateStatus( 0 )
                self.enPressure.setData( "n/a" )
                
            if portPCSStatus == 1:
                self.frPCS.ltActive.updateStatus( outputStatus )
                self.enSetpoint.setData( '{:.2e}'.format(setpoint) )
                self.btSet.updateStatus( 1 )
                if portL392Status == 1:
                    if outputStatus == 1:
                        self.btOutput.updateStatus( 1 )
                    else:
                        self.btOutput.updateStatus( -1 )
                else:
                    self.btOutput.updateStatus( 0 )
            else:
                self.btSet.updateStatus( 0 )
                self.btOutput.updateStatus( 0 )
                self.frPCS.ltActive.updateStatus( 0 )
                self.enSetpoint.setData( 'n/a' )
            
        
        # Plot section
        if plotVal == 'pressure':
            if portL392Status == 1:
                self.btPlotPressure.setActive()
                self.btPlotBiasVoltage.setDeactive()
                self.btPlotBiasCurrent.setDeactive()
                self.btPlotHeat.setDeactive()
                self.updatePlot( plotPressureData, plotVal )
            else:
                pass
        elif plotVal == 'biasV':
            self.btPlotPressure.setDeactive()
            self.btPlotBiasVoltage.setActive()
            self.btPlotBiasCurrent.setDeactive()
            self.btPlotHeat.setDeactive()
            self.updatePlot( plotBiasVData, plotVal )
        elif plotVal == 'biasI':
            self.btPlotPressure.setDeactive()
            self.btPlotBiasVoltage.setDeactive()
            self.btPlotBiasCurrent.setActive()
            self.btPlotHeat.setDeactive()
            self.updatePlot( plotBiasIData, plotVal )
        elif plotVal == 'heat':
            self.btPlotPressure.setDeactive()
            self.btPlotBiasVoltage.setDeactive()
            self.btPlotBiasCurrent.setDeactive()
            self.btPlotHeat.setActive()
            self.updatePlot( plotHeatData, plotVal )
        else:
            print("PCS Plot Variable in indeterminate state. Check??")

            
         

    
    def initPlotFrame(self):
        self.fig = Figure(figsize = (6,3), dpi=100)  #, tight_layout=True)
        self.ax = self.fig.add_axes([.15, .15, .75, .7], polar=False)
        self.ax.set_title('Pressure v. Time')
        self.ax.set_xlabel('Time since start (s)')
        self.ax.set_ylabel('Pressure (Torr)')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frPlot)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row = 1, column = 0, columnspan = 5)
        
    def updatePlot(self, plotData, plotVal):
        # revisit this!!
        try:
            self.ax.clear()
            # print(plotData)
            # print("Length of Data is ", len(plotData))
            if len(plotData) > 1:

                frmt = md.DateFormatter('%H:%M:%S')
                # ax = plt.gca()
                self.ax.xaxis.set_major_formatter(frmt)
                # print("yeyee")
                
                times = md.date2num([dt.datetime.fromtimestamp(ts) for ts in plotData[:,0]])
                # print('hahw')
                if plotVal == 'heat':
                    # self.ax.plot(times, plotData[:,1])
                    self.ax.plot(times, plotData[:,1], 'y-', label='Heat 1')
                    self.ax.plot(times, plotData[:,2], 'g-', label='Heat 2')
                    self.ax.plot(times, plotData[:,3], 'k--', label='Average')
                    self.ax.legend(loc="upper left")
                else: # Normal
                    self.ax.plot(times, plotData[:,1])
                    self.ax.ticklabel_format(style='sci', axis='y', scilimits = (0,0))
                    
                    
                self.ax.autoscale(axis='y')
                self.ax.tick_params(axis='x', labelrotation=25)
                    # print('!')
            else:
                self.ax.plot()
                # print("No data to plot :(")
            


            if plotVal == 'pressure':
                self.ax.set_title('Pressure v. Time')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Pressure (Torr)')
            elif plotVal == 'biasV':
                self.ax.set_title('Bias Voltage v. Time')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Bias Voltage (V)')
            elif plotVal == 'biasI':
                self.ax.set_title('Bias Current v. Time')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Bias Current (A)')
            elif plotVal == 'heat':
                self.ax.set_title('Source Temperature v. Time')
                self.ax.set_xlabel('Time (s)')
                self.ax.set_ylabel('Temperature (K)')
                
            self.canvas.draw()
        except:
            print(" failed to update ", plotVal, " Plot" )   
        
        


class LeskerCOMFrame( ttk.Frame ):
    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'l392'
        
        self.columnconfigure( index=0, weight=0 )
        self.rowconfigure( index=0, weight=1 )
        
    def initWidgets(self):
        
        self.listCOM = PortSelectorBox( self, self.name )
        self.btConnect = ConnectButton( self, self.name+'connect' )
        self.ltCOM = StatusLight( self, self.name + 'com' )
        self.ltActive = StatusLight( self, self.name + 'ig' )
        
        self.lblPort = ttk.Label( self, text = 'Lesker 392:', style = 'Std.TLabel')
        self.lblCOMStatus = ttk.Label( self, text = 'Lesker COM', style = 'Std.TLabel')
        self.lblIG = ttk.Label( self, text = 'IG Filaments', style = 'Std.TLabel')

        self.lblPort.grid( row = 0, column = 1 )
        self.listCOM.grid( row = 0, column = 2 )
        self.btConnect.grid( row = 0, column = 3, padx = 5 )
        self.ltCOM.grid( row = 1, column = 0 )
        self.lblCOMStatus.grid( row = 1, column = 1 )
        self.ltActive.grid( row = 2, column = 0 )
        self.lblIG.grid( row = 2, column = 1 )
    
    


class PCSCOMFrame( ttk.Frame ):
    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'pcs'
        
        self.columnconfigure( index=0, weight=0 )
        self.rowconfigure( index=0, weight=1 )
        
    def initWidgets(self):
        self.listCOM = PortSelectorBox( self, self.name )
        self.btConnect = ConnectButton( self, self.name+'connect' )
        self.ltCOM = StatusLight( self, self.name + 'com' )
        self.ltActive = StatusLight( self, self.name + 'output' )
        
        
        self.lblPort = ttk.Label( self, text = 'Pressure\nController:', style = 'Std.TLabel')
        self.lblCOMStatus = ttk.Label( self, text = 'PCS COM', style = 'Std.TLabel')
        self.lblOutput = ttk.Label( self, text = 'PCS Active', style = 'Std.TLabel')
        
        self.lblPort.grid( row = 0, column = 0 )
        self.listCOM.grid( row = 0, column = 1 )
        self.btConnect.grid( row = 0, column = 2, padx = 5 )
        self.lblCOMStatus.grid( row = 1, column = 2 )
        self.ltCOM.grid( row = 1, column = 3 )
        self.lblOutput.grid( row = 2, column = 2 )
        self.ltActive.grid( row = 2, column = 3 )