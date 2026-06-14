import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from VCP_GUI_Elements import *
import numpy as np

class PlotFrame( ttk.Frame ):
    #Constructor
    def __init__(self, parent ): #, listCOM, btConnect, btMove, btStop, ltCOM, ltMove, enInputZ, enInputT):
        super().__init__(parent)
        self.name ='frPlot'
        self.plotType = ''
        # try:
        #     self.grid_propagate(0)
        #     self['width'] = round(parent.winfo_screenwidth()/2)
        #     self['height'] = round((parent.winfo_screenheight()-50)/2)
        # except:
        #     print("don't like me")
        self['borderwidth'] = 1
        self['relief'] = 'solid'
            
    def initWidgets(self):

        self.frButtons = ttk.Frame( self )
        self.frPlot = ttk.Frame( self )
        
        self.lblTitle = ttk.Label( self.frButtons, text = "Plot:", style = 'Header.TLabel')
        self.lblSweepNum = ttk.Label( self.frButtons, text = 'Sweep #:', style = 'Std.TLabel' )
        
        self.listSweepNum = SweepSelectorBox( self.frButtons, 'NumSweepBox' )
        self.listChNum = SweepSelectorBox( self.frButtons, 'NumChBox' )
        
        self.btPlotSweepProfile = ClickButton( self.frButtons, 'PlotProfile')
        self.btPlotAllSweeps = ClickButton( self.frButtons, 'PlotAllButtons')
        # self.btPlotIV = ClickButton( self.frButtons, 'PlotIV' )
        self.btPlotCh1 = ClickButton( self.frButtons, 'PlotCh1')
        self.btPlotCh2 = ClickButton( self.frButtons, 'PlotCh2')
        self.btPlotdI1 = ClickButton( self.frButtons, 'PlotdI1')
        self.btPlotdI2 = ClickButton( self.frButtons, 'PlotdI2')
        self.btPlotEEDF = ClickButton( self.frButtons, 'PlotEEDF')
        
        # self.btPlotIV.grid(row = 1, column = 0)

        self.initLocations()
        self.initPlotFrame()
        
    def initLocations(self):
        self.columnconfigure( index=0, weight=1 )
        self.rowconfigure( index=0, weight=1 )
              
        self.frPlot.grid( row = 0, column = 0 )
        
        self.frButtons.grid( row = 0, column = 1, sticky = 'nsew' )
        self.frButtons['relief'] = 'raised'
        self.frButtons.columnconfigure( index=0, weight=1 )
        self.frButtons.rowconfigure( index=0, weight=0 )
        self.frButtons.rowconfigure( index=1, weight=3 )
        self.frButtons.rowconfigure( index=4, weight=1 )
        self.frButtons.rowconfigure( index=5, weight=1 )
        self.frButtons.rowconfigure( index=6, weight=1 )
        self.frButtons.rowconfigure( index=7, weight=1 )
        self.frButtons.rowconfigure( index=8, weight=1 )
        self.frButtons['padding'] = ('0.25c', '0.5c')
        
        
        self.lblTitle.grid(row = 0, column = 0)
        
        self.btPlotSweepProfile.grid( row = 1, column = 0 )
        
        self.lblSweepNum.grid( row = 2, column = 0 )
        self.listSweepNum.grid(row = 3, column = 0)
        self.btPlotCh1.grid(row = 4, column = 0)
        self.btPlotCh2.grid(row = 5, column = 0)
        self.btPlotdI1.grid(row = 6, column = 0)
        self.btPlotdI2.grid(row = 7, column = 0)
        self.btPlotEEDF.grid(row = 8, column = 0)
        
        
        
    def updateWidgets( self, ch1, ch2, boardID, autoMode, flgCOM ):
        # print("updateWidget() method called for plot frame")
        # "Updates" (replots) whatever was previously plotted
        
        if ch1.any():
            self.listSweepNum.createList( np.shape(ch1), boardID )
            if self.listSweepNum.get() == '':
                self.listSweepNum.set('Sweep #1')
                
        
        # if autoMode == 1 and flgCOM == 1:
        #     self.updatePlot(ch1, ch2)
            
    def updatePlot( self, ch1, ch2, E, Ge, boardID, header, subtitle ):
        # print("Plot type ", self.plotType)
        if ch1.any():
            if self.plotType == '1':
                self.plotSingleIV( ch1, 1, self.listSweepNum.getSelection(), boardID, header, subtitle )
            elif self.plotType == '2':
                self.plotSingleIV( ch2, 2, self.listSweepNum.getSelection(), boardID, header, subtitle )
            elif self.plotType == 'dI1':
                self.plotSingledIdV( ch1, 1, self.listSweepNum.getSelection(), boardID, header, subtitle )
            elif self.plotType == 'dI2':
                self.plotSingledIdV( ch2, 2, self.listSweepNum.getSelection(), boardID, header, subtitle )
            elif self.plotType == 'EEDF':
                self.plotEEDF( E, Ge, self.listSweepNum.getSelection(), subtitle )
            elif self.plotType == 'p':
                # self.plotSweepProfile()
                pass
            elif self.plotType == '': # In case nothing has been 
                self.plotSingleIV( ch1, 1, 0, boardID, header, subtitle )
            else:
                pass
        
    def initPlotFrame(self):
        self.fig = Figure(figsize = (7,4), dpi=100)  #, tight_layout=True)
        self.ax = self.fig.add_subplot(111)  #add_axes([.15, .15, .75, .7], polar=False)


        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frPlot)
        
        self.canvas.get_tk_widget().grid(row = 0, column = 0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frPlot, pack_toolbar=False)
        self.toolbar.grid(row = 1, column = 0)
        self.toolbar.update()
        
        self.canvas.draw()
        
    def plotSweepProfile(self, profile):
        # print("profile: ", profile)
        try:
            self.ax.clear()
            self.ax.scatter(np.arange(1, np.size(profile, 0)+1),  profile, marker='.')
            self.ax.set_xlabel('Index')
            self.ax.set_ylabel('Counts')
            self.ax.set_title("WSLP Sweep Profile")
            
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = 'p'
            # self.toolbar.update()
        except:
            print("Can't plot sweep profile, error is ")
    
    
    def plotSingleIV(self, ch, chNum, sweepNum, boardID, header, subtitle):
        # print( "single IV plot method: ", ch, chNum, sweepNum, boardID, header, subtitle)
        try:
            self.ax.clear()
            if boardID == 1: # WSLP 2.1 - outdated
                half = int(np.size(ch, 0)/2)
                self.ax.plot(ch[0:half,1,sweepNum],  ch[0:half,2,sweepNum]*1e6, 'r-', label='Upsweep {:d}'.format(sweepNum+1))
                self.ax.plot(ch[half:-1,1,sweepNum],  ch[half:-1,2,sweepNum]*1e6, color='black', label='Downsweep {:d}'.format(sweepNum+1))                
                if chNum == 1:
                    self.fig.suptitle("WSLP Unity Ch. - Sweep #{:d}".format(sweepNum+1))
                elif chNum == 2:
                    self.fig.suptitle("WSLP High Gain Ch. - Sweep #{:d}".format(sweepNum+1))
                    self.ax.axhline(y=0, color = 'black', linestyle='dashed')
                else:
                    self.fig.suptitle("WSLP Ch{:d} - Sweep #{:d}".format(chNum, sweepNum+1))
                    print("Error in plotSingleIV: chNum is neither 1 nor 2")
                    
            if boardID == 2: # WSLP v2.2 - yeehaw
                # sweep num comes in as value used in Header: 0:#legs
                # print("sweepNum is ", sweepNum)
                name1 = 'Sweep_'+str(sweepNum)
                name2 = 'Sweep_'+str(sweepNum+1)
                # print("names 1&2 = ", name1, ', ', name2)
                # print("size for n1 is ", np.shape(ch[:,:,sweepNum]) )
                # print("size for n2 is ", np.shape(ch[:,:,sweepNum+1]) )
                # print("first plot's size vectors are ", np.shape(ch[ :,2,sweepNum ]), ", and ", np.shape(ch[ :,3,sweepNum ])  )
                # print(" thing: ",  ch[ 0:10,2,sweepNum ], ch[ 0:10,3,sweepNum ])
                # print("sweepnum is ", sweepNum)
                l1, = self.ax.plot(ch[ :,2,sweepNum ].T, ch[ :,3,sweepNum ].T*1e6)
                if header[name1]['sweepDirection'] == 'Up':
                    l1.set_color('red')
                elif header[name1]['sweepDirection'] == 'Down':
                    l1.set_color('black')
                elif header[name1]['sweepDirection'] == 'Hold':
                    l1.set_color('blue')
                l1.set_label( header[name1]['sweepDirection']+' sweep, leg #{:d}'.format(int(sweepNum)) )

                # l2, = self.ax.plot(ch[:,3,2*sweepNum+1],  ch[:,4,2*sweepNum+1]*1e6, color='black', label='Downsweep {:d}'.format(sweepNum+1))
                l2, = self.ax.plot(ch[ :,2,sweepNum+1 ], ch[ :,3,sweepNum+1 ]*1e6)
                if header[name2]['sweepDirection'] == 'Up':
                    l2.set_color('red')
                elif header[name2]['sweepDirection'] == 'Down':
                    l2.set_color('black')
                elif header[name2]['sweepDirection'] == 'Hold':
                    l2.set_color('blue')
                l2.set_label( header[name2]['sweepDirection']+' sweep, leg #{:d}'.format(int(sweepNum+1)) )
                
                self.ax.legend(loc="upper left")
                if chNum == 1:
                    self.fig.suptitle("WSLP Unity Ch. - Sweep #{:d}".format(int(sweepNum/2 + 1))) 
                elif chNum == 2:
                    self.fig.suptitle("WSLP High Gain Ch. - Sweep #{:d}".format(int(sweepNum/2 +1)) )
                    self.ax.axhline(y=0, color = 'black', linestyle='dashed', linewidth = 0.5)
                else:
                    self.fig.suptitle("WSLP Ch{:d} - Sweep #{:d}".format(chNum, int(sweepNum/2 + 1)) )
                    print("Error in plotSingleIV: chNum is neither 1 nor 2")
                    
            ylim = self.ax.get_ylim()
            textYMax = (ylim[1] - ylim[0] )
            try:
                self.ax.text( -35, textYMax*0.75+ ylim[0], 'Est. Ne: {:.1e}, {:.1e} m$^-3$ \n Est. Te: {:.1f}, {:.1f} eV'.format(header[name1]['estNe'], header[name2]['estNe'],header[name1]['estTeeV'], header[name2]['estTeeV'] ))
            # self.ax.text( -35, textYMax*0.7, ''.format( ))
            except:
                pass
                    
            self.ax.set_xlabel('Volts')
            self.ax.set_ylabel('Current (µA)')
            if not subtitle == '':
                self.ax.set_title(subtitle)
            # self.ax.legend(loc='upper left')
            # print("got titles in")
            
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = '{:d}'.format(chNum)
            # print("Plotted ", self.plotType)
        except Exception as err:
            print("Can't plot single IV, error is ", err)
            
    def plotSingledIdV(self, ch, chNum, sweepNum, boardID, header, subtitle):
        try:
            self.ax.clear()
            if boardID == 1:
                half = int(np.size(ch, 0)/2)
                dV = ch[half,1,sweepNum] - ch[half-2,1,sweepNum]
                self.ax.plot(ch[0:half-1,1,sweepNum]+(dV/2),  np.diff(ch[0:half,2,sweepNum]*1e6,axis=0)/dV, 'r-', label='Upsweep {:d}'.format(sweepNum+1))
                self.ax.plot(ch[half+1:-1,1,sweepNum]+(dV/2),  np.diff(ch[half:-1,2,sweepNum]*1e6,axis=0)/dV, color='black', label='Downsweep {:d}'.format(sweepNum+1))
            
                if chNum == 1:
                    self.fig.suptitle("WSLP Unity Ch. - dI/dV for Sweep #{:d}".format( int(sweepNum+1) ))
                elif chNum == 2:
                    self.fig.suptitle("WSLP High Gain Ch. - dI/dV for Sweep #{:d}".format( int(sweepNum+1) ))
                else:
                    self.fig.suptitle("WSLP Ch{:d} - dI/dV for Sweep #{:d}".format(chNum, int(sweepNum+1) ))
                    print("Error in plotSingleIV: chNum is neither 1 nor 2")
            elif boardID == 2:
                print("Sweepnum is ", sweepNum)
                name1 = 'Sweep_'+str(sweepNum)
                name2 = 'Sweep_'+str(sweepNum+1)
                # dV = ch[-1,1,sweepNum] - ch[-2,1,sweepNum]
                V = ch[:,2,sweepNum]
                l1, = self.ax.plot( V, np.gradient(ch[ :,3,sweepNum], V )*1e6 ) #np.diff(ch[ :,3,sweepNum]*1e6,axis=0)/dV )
                if header[name1]['sweepDirection'] == 'Up':
                    l1.set_color('red')
                elif header[name1]['sweepDirection'] == 'Down':
                    l1.set_color('black')
                elif header[name1]['sweepDirection'] == 'Hold':
                    l1.set_color('blue')
                l1.set_label( header[name1]['sweepDirection']+' sweep, leg #{:d}'.format(int(sweepNum)))
                
                # print(dV)
                l2, = self.ax.plot( V, np.gradient(ch[ :,3,sweepNum], V )*1e6 )
                if header[name2]['sweepDirection'] == 'Up':
                    l2.set_color('red')
                elif header[name2]['sweepDirection'] == 'Down':
                    l2.set_color('black')
                elif header[name2]['sweepDirection'] == 'Hold':
                    l2.set_color('blue')
                l2.set_label( header[name2]['sweepDirection']+' sweep, leg #{:d}'.format(int(sweepNum+1)) )
                
                if chNum == 1:
                    self.fig.suptitle("WSLP Unity Ch. - dI/dV for Sweep #{:d}".format( int(sweepNum/2+1)) )
                elif chNum == 2:
                    self.fig.suptitle("WSLP High Gain Ch. - dI/dV for Sweep #{:d}".format( int(sweepNum/2+1)) )
                else:
                    self.fig.suptitle("WSLP Ch{:d} - dI/dV for Sweep #{:d}".format(chNum, int(sweepNum/2+1)) )
                    print("Error in plotSingleIV: chNum is neither 1 nor 2")
            
            self.ax.set_xlabel('Volts')
            self.ax.set_ylabel('Differential Current (µA/V)')
            self.ax.axvline(x=header[name1]['estVp'], color = 'black', linewidth = 0.25)
            
            if not subtitle == '':
                self.ax.set_title(subtitle)
                
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = 'dI{:d}'.format(chNum)
        except Exception as err:
            print("Can't plot sweep profile, error is ", err)

    def plotEEDF(self, E, Ge, sweepNum, subtitle):
        try:
            self.ax.clear()

            name1 = 'Sweep_'+str(sweepNum)
            name2 = 'Sweep_'+str(sweepNum+1)
            l1, = self.ax.plot(E[name1], Ge[name1])
            # if header[name1]['sweepDirection'] == 'Up':
            # l1.set_color('red')
            # elif header[name1]['sweepDirection'] == 'Down':
                # l1.set_color('black')
            # elif header[name1]['sweepDirection'] == 'Hold':
            l1.set_color('blue')
            l1.set_label( 'Sweep leg #{:d}'.format(int(sweepNum)) )
    
            # l2, = self.ax.plot(ch[:,3,2*sweepNum+1],  ch[:,4,2*sweepNum+1]*1e6, color='black', label='Downsweep {:d}'.format(sweepNum+1))
            l2, = self.ax.plot(E[name2], Ge[name2])
            # if header[name2]['sweepDirection'] == 'Up':
                # l2.set_color('red')
            # elif header[name2]['sweepDirection'] == 'Down':
            l2.set_color('black')
            # elif header[name2]['sweepDirection'] == 'Hold':
                # l2.set_color('blue')
            l2.set_label( 'Sweep leg #{:d}'.format(int(sweepNum+1)) )
            
            self.ax.legend(loc="upper right")
            self.fig.suptitle("EEDF - Sweep #{:d}".format(int(sweepNum/2 + 1))) 

            ylim = self.ax.get_ylim()
            xlim = self.ax.get_xlim()
            textYMax = (ylim[1] - ylim[0] )
            textXMax = (xlim[1] - xlim[0] )
            try:
                self.ax.text( textYMax*0.75, textYMax*0.75+ ylim[0], 'Est. Ne: {:.1e}, {:.1e} m$^-3$ \n Est. Te: {:.1f}, {:.1f} eV'.format(header[name1]['estNe'], header[name2]['estNe'],header[name1]['estTeeV'], header[name2]['estTeeV'] ))
            # self.ax.text( -35, textYMax*0.7, ''.format( ))
            except:
                pass
                    
            self.ax.set_xlabel('E')
            self.ax.set_ylabel('Ge')
            if not subtitle == '':
                self.ax.set_title(subtitle)
            # self.ax.legend(loc='upper left')
            # print("got titles in")
            
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = 'EEDF' 
        except Exception as err:
            print("Can't plot EEDF, error is ", err)
        
        
# Depreciated
    def plotCh1(self, ch, sweepNum):
        try:
            self.ax.clear()
            half = int(np.size(ch, 0)/2)
            self.ax.plot(ch[0:half,1,sweepNum],  ch[0:half,2,sweepNum]*1e6, 'r-', label='Upsweep {:d}'.format(sweepNum+1))
            self.ax.plot(ch[half:-1,1,sweepNum],  ch[half:-1,2,sweepNum]*1e6, color='black', label='Downsweep {:d}'.format(sweepNum+1))
            self.ax.set_xlabel('Volts')
            self.ax.set_ylabel('Current (µA)')
            self.ax.set_title("WSLP Unity Channel - Sweep #{:d}".format(sweepNum+1))
            # self.ax.legend(loc='upper left')
            # print("got titles in")
            
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = '1'
        except Exception as err:
            print("Can't plot sweep profile, error is ", err)
            
    def plotAllCh1(self, ch):
        # print("plotCh1() method called in PlotFrame")
        try:
            self.ax.clear()
            half = int(np.size(ch, 0)/2)
            for i in range(np.size(ch, 2)):
                # red up, black down
                self.ax.plot(ch[0:half,0,i],  ch[0:half,1,i], 'r-', label='Upsweep {:d}'.format(i))
                self.ax.plot(ch[half:-1,0,i],  ch[half:-1,1,i], color='black', label='Downsweep {:d}'.format(i))
            self.ax.set_xlabel('dac Counts')
            self.ax.set_ylabel('ADC Counts')
            self.ax.set_title("WSLP Unity Sweep data")
            self.ax.legend(loc='upper left')
            # print("got titles in")
            
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = '1'
            # print("drawed")
            # self.toolbar.update()
        except Exception as err:
            print("Can't plot sweep profile, error is ", err)
        
    def plotAllCh2(self, ch):
        # print("plotCh1() method called in PlotFrame")
        try:
            self.ax.clear()
            half = int(np.size(ch, 0)/2)
            for i in range(np.size(ch, 2)):
            
                self.ax.plot(ch[0:half,0,i],  ch[0:half,1,i], 'r-', label='Upsweep {:d}'.format(i))
                self.ax.plot(ch[half:-1,0,i],  ch[half:-1,1,i], color='black', label='Downsweep {:d}'.format(i))
            self.ax.set_xlabel('dac Counts')
            self.ax.set_ylabel('ADC Counts')
            self.ax.set_title("WSLP Ch2 Sweep data")
            self.ax.legend(loc='upper left')
            
            self.toolbar.update()
            self.canvas.draw()
            self.plotType = '2'
        except Exception as err:
            print("Can't plot sweep profile, error is ", err)
