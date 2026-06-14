import sys, os,base64
from icon import img
from datetime import date
import time as t
from datetime import datetime
import pandas
from pathlib import Path
from scipy import io as sio

class Directory():
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.parent = os.path.dirname(sys.executable)
        else:
            try:
                app_full_path = os.path.realpath(__file__)
                self.parent = os.path.dirname(app_full_path)
            except NameError:
                self.parent = os.getcwd()
                
        # Where bundled resources live (PyInstaller: onefile extracts to sys._MEIPASS)
        self.bundle_dir = getattr(sys, "_MEIPASS", self.parent)

        # Read-only resources (from --add-data "images;images")
        self.images = os.path.join(self.bundle_dir, "images")
        self.logs = self.parent + '\\Logs'
        self.data = self.parent + '\\Exp_Data'
        
        #Path(self.images).mkdir(exist_ok=True)
        Path(self.logs).mkdir(exist_ok=True)
        Path(self.data).mkdir(exist_ok=True)
        
class FilamentTimeManager():
    def __init__(self):
        self.filename = Directory().data + '\\' + "FilamentUseTime.mat"
        self.lastTimeStamp = round( datetime.now().timestamp() )
        
    def updateFilamentUseTime(self, heat1Temp, heat2Temp):
        # ASSUMES FILS AT SAME TEMPERATURE FOR ENTIRE LAST TIME PERIOD
        self.loadBins()
        timeNow = round( datetime.now().timestamp() )
        dT = timeNow - self.lastTimeStamp
        if heat1Temp > 1500:
            self.sortBin( '1', heat1Temp, dT )
        if heat2Temp > 1500:
            self.sortBin( '2', heat2Temp, dT )
        self.lastTimeStamp = timeNow
        self.saveBins()
        
    def loadBins(self):
        try:
            data = sio.loadmat(self.filename, simplify_cells=True)
            self.timeBins = {'1':data['heat1Bins'], '2':data['heat2Bins']}
            self.lastTimeStamp = data['lastTimeStamp']
        except:
            print("error opening Filament Timer file")
            return
        
    def sortBin(self, heatNumber, temp, dT): # heatNumber is string character
        if temp <= 1850:
            binn = "in<1850"
        elif temp > 1850 and temp <= 2000:
            binn = "in1851_2000"
        elif temp > 2000 and temp <= 2150:
            binn = "in2001_2150"
        elif temp > 2150 and temp <= 2200:
            binn = "in2151_2200"
        elif temp > 2200 and temp <= 2250:
            binn = "in2201_2250"
        elif temp > 2250 and temp <= 2300:
            binn = "in2251_2300"
        elif temp > 2300:
            binn = "in>2301"
        else:
            binn = 'unknown'
        self.timeBins[heatNumber][binn] = self.timeBins[heatNumber][binn] + dT
            
        # print("Modified for heatNumber ", heatNumber)
        
    def saveBins(self):
        try:
            sio.savemat(self.filename, {'heat1Bins':self.timeBins['1'], 'heat2Bins':self.timeBins['2'], 'lastTimeStamp':self.lastTimeStamp })
        except:
            print("error opening Filament Timer file")
        return
        
        # This class is for keeping track of the filament use time
        # attributes: path/file, heat1 temp, heat1 time, heat 2 temp/time
        # methods: update time (pull values from .mat file, bin, upload .mat file)\
        #                               where bin means dTime at same temp then add to file
        # .mat bin:
            # contained times for <1850, 1850-2000, 2000-2150, 2150-2200, 2200-2250, 2250-2300, >2350
        
        
        
        
def setIcon(self):
        tmp = open("tmp.ico", "wb+")
        tmp.write(base64.b64decode(img))
        tmp.close()
        self.iconbitmap("tmp.ico")
        os.remove("tmp.ico")

class BreakAllLoops( Exception ): # ?
    pass

class ExcelManager():
    def __init__(self):
        self.path = Directory().logs + '\\'
        self.numData = 0
        self.saveNum = 5*60 # 5min in seconds
        self.columnHeaders = ['Time', 'Pressure', 'PCS Setpoint', 'Motor Z', 'Motor T', 'Heat1 Setpoint', 'Heat1, V', 'Heat1, A', 'Heat 1, T', 'Heat2 Setpoint', 'Heat2, V', 'Heat2, A', 'Heat2, T', 'Bias Setpoint', 'Bias, V', 'Bias, A', 'Bx', 'By', 'Bz']
        self.dataCache = pandas.DataFrame([], columns=self.columnHeaders)
        
        
    def fileName(self):
        today = date.today()
        name = 'SAIL_Chamber_Log_' + today.strftime("%m-%d-%Y") + '.csv'
        return name


    def saveData(self, dataData, connectionData, activeData):
        # Every time its called, it will add the data to a cache
        # After a set time, the cache will be saved to CSV 
        path = self.path + self.fileName()

        # Make if DNE
        if not os.path.isfile(path):
            self.dataCache = pandas.DataFrame([], columns=self.columnHeaders)
            self.dataCache.to_csv(path, index=False, header=True)

        # Timestamp
        dataData['Time'] = [t.strftime('%H:%M:%S')]
        dataData = pandas.DataFrame(self.clearUnusedData(connectionData, activeData, dataData) )
        
        # Save to cache
        try:
            self.dataCache = pandas.concat( [self.dataCache, dataData], ignore_index=True)
            self.numData = self.numData + 1
        except:
            print("error saving data to cache")
            
        # Save every couple min 
        try:
            if self.numData > self.saveNum:
                # df = pandas.DataFrame(self.dataCache)
                self.dataCache.to_csv( path, index=False, header = False, mode = 'a' )
                self.dataCache = self.dataCache[0:0] # clear rows, keep columns
                self.numData = 0
                print('saved!')
        except:
            print("Error saving data to CSV (is file open?)")
            
    def clearUnusedData(self, connectionData, activeData, dataData):
        # Conditionally save data
        #self.names = [ 'mc', 'l392', 'pcs', 'heat1','heat2', 'bias', 'wslp' ]
        if connectionData['l392'] != 1:
            dataData['Pressure'] = ''
        # print("PCS connection is", connectionData['pcs'], ' and active flag is ', activeData['pcs'])
        if connectionData['pcs'] != 1 or activeData['pcs']  != 1:
            # This doesn't work? always reads as 0 in logs
            dataData['PCS Setpoint'] = ''
            # print("data for setpoint is ", dataData['PCS Setpoint'])
        if connectionData['mc'] != 1:
            dataData['Motor Z'] = ''
            dataData['Motor T'] = ''
        if activeData['heat1'] != 1:
            dataData['Heat1 Setpoint'] = ''
        if connectionData['heat1'] != 1:
            dataData['Heat1, V'] = ''
            dataData['Heat1, A'] = ''
            dataData['Heat1, T'] = ''
        if activeData['heat2'] != 1:
            dataData['Heat2 Setpoint'] = ''
        if connectionData['heat2'] != 1:
            dataData['Heat2, V'] = ''
            dataData['Heat2, A'] = ''
            dataData['Heat2, T'] = ''
        if activeData['bias'] != 1:
            dataData['Bias Setpoint'] = ''
        if connectionData['bias'] != 1:
            dataData['Bias, V'] = ''
            dataData['Bias, A'] = ''
        if connectionData['pni'] != 1:
            dataData['Bx'] = ''
            dataData['By'] = ''
            dataData['Bz'] = ''
        
        return dataData


# data = {'Time':['8:16'],
#         'Pressure':1, 'PCS setpoint':2, 'Motor Z':100, 'Motor T':0, 'Heat1 Setpoint':1, 'Heat1, V':1, 'Heat1, A':0, 'Heat2 Setpoint':1, 'Heat2, V':1, 'Heat2, A':1, 'Bias Setpoint':1, 'Bias, V':1, 'Bias, A':0 }
# x.saveData( data )






























