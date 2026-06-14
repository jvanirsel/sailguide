from Basic import PeripheralDevice
from threading import Thread, Condition
from time import sleep
from math import ceil
import numpy as np
from scipy.optimize import minimize_scalar
import pickle
from misc import Directory

class BKP9115( PeripheralDevice ):
    def __init__(self, name):
        super().__init__( name, 115200, '\r\n', 2)
        # self.numFilaments = numFilaments
        #More attributes here
        self.current = 0.0
        self.voltage = 0.0
        self.power = 0.0
        self.temperature = 0.0
        self.setVoltage = 0.0
        self.setCurrent = 0.0
        self.targetVoltage = 0.0
        self.targetCurrent = 0.0
        self.biasCurrent = 0.0 # Unnecessary
        self.flgActive = -1
        
        try:
            with open(Directory().data + '\\FilamentParams.pkl', 'rb') as file:
                FilamentParams = pickle.load(file)
            self.R300 = FilamentParams[self.name]['R300']
            self.R_leftover = FilamentParams[self.name]['Roff']
        except:
            print("Error loading Filament Calibration file on ", self.name)
        
    ### Methods ###
    # Overwritten Methods:
    def validateConnection(self):
        print( 'validateConnection() method called from ' + self.name )
        buf = self.command( '*IDN?', 50 )
        # print('buf is ', buf, " of length ", len(buf))
        if( buf[0:19] != b'B&K Precision, 9115' ):
            return True
        else:
            print("Non-valid BKP connection; ret = ", buf)
            return False
        
        return False
    def doConnect(self):
        super().doConnect()
        self.setRemoteControl()
        if self.name == 'Bias':
            self.setRamp(60)
        else:
            self.setRamp(1800)
        
    def disconnect(self):
        self.doSetLocalControl()
        super().disconnect()
        
        
    def pollSystemData(self):
        # print( 'pollSystemData() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*4) )
        # meas I,v, setpoints, output
        # return true unless it breaks
        ret = False
        try:
            self.voltage = float( (self.command( 'MEAS:VOLT?' ).decode())[0:-1] )
            self.current = float( (self.command( 'MEAS:CURR?' ).decode())[0:-1] )
            self.power = round(self.voltage*self.current,1)
            self.calcTemp()
            self.setVoltage = float( (self.command( 'SOUR:VOLT?' ).decode())[0:-1] )
            self.setCurrent = float( (self.command( 'SOUR:CURR?' ).decode())[0:-1] )
            if int(self.command( 'SOUR:OUTP?' ).decode()[0:-1]):
                self.flgActive = 1
            else:
                self.flgActive = -1
            ret = True
        except:
            print("goof on BKP ", self.name)
        self.cv.release()
        return ret
            
    # Unique Methods:
    def calcTemp(self):
        if self.name != 'Bias':
            try: # Righini Resistance Method
                R = self.voltage / ((self.current) + 1e-3) # +1e-3 to prevent divide by 0 error
                Rratio = (R - self.R_leftover)/(self.R300 - self.R_leftover)
                a = 357.841525795891
                b = 106.045169111230
                c = 10.0662442587009
                d = -0.695146143317883
                e = 0.0152225901966301
                temp = a + b*Rratio + c*(Rratio**2) + d*(Rratio**3) + e*(Rratio**4)
                
                # Don't trust anything much above 2900 K
                if temp > 2900:
                    temp = 2900
                if self.power < 75: # Less than 75W is negligible
                    temp = 0
                
                self.temperature = round(temp,-1) # Round to 10s place, since it isn't that accurate anyways
            except:
                print("Error calculating temperature.")
                self.temperature = -1
        return
    
    
    def setOutput(self, newParam, paramType):
        print( 'setOutput() method called from ' + self.name )
        if(self.comStatus == 1):
            self.thSetOutput = Thread( target = self.doSetOutput, name = self.name + '-Set-Output', daemon = True, args=(newParam, paramType,))
            self.thSetOutput.start()
            return True
        else:
            print( self.name, " is not connected; enableIG command not executed" )
            return False
        
    def doSetOutput(self, newV, newI):
        print( 'doSetOutput() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        try:
            if newI:
                self.setTargetCurrent( newI )
            self.setTargetVoltage( newV )
            if not newI:
                self.setTargetCurrent()
            self.command( 'SOUR:APPL {:.3f}, '.format(self.targetVoltage) + '{:.3f}'.format(self.targetCurrent), 0 )
            self.checkError()
        except:
            pass
        self.cv.release()
        
    def enableOutput(self):
        print( 'enableOutput() method called from ' + self.name )
        if(self.comStatus == True):
            self.thEnableOutput = Thread( target = self.doEnableOutput, name = self.name + '-Enable-Output', daemon = True )
            self.thEnableOutput.start()
            return True
        else:
            print( self.name, " is not connected; enableIG command not executed" )
            return False
        
    def doEnableOutput(self):
        print( 'doEnableOutput() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        self.command( 'SOUR:OUTP ON', 0 )
        self.checkError()
        self.cv.release()
        
    def disableOutput(self):
        print( 'disableOutput() method called from ' + self.name )
        if(self.comStatus == True):
            self.thDisableOutput = Thread( target = self.doDisableOutput, name = self.name + '-Disable-Output', daemon = True )
            self.thDisableOutput.start()
            return True
        print( self.name, " is not connected; enableIG command not executed" )
        return False
        
    def doDisableOutput(self):
        print( 'doDisableOutput() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        self.command( 'SOUR:OUTP OFF', 0 )
        self.checkError()
        self.cv.release()
        
    def setRamp(self, goalTime):
        print( 'ramp() method called from ' + self.name )
        if self.comStatus == True:
            self.thRamp = Thread( target = self.doSetRamp, name = self.name + '-Ramp', daemon = True, args=(goalTime,) )
            self.thRamp.start()
            return True
        else:
            print( self.name, " is not connected; setRamp command not executed" )
            return False
        
    def doSetRamp(self, goalTime):
        print( 'doRamp() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*2.25) )
        self.command( 'SOUR:RIS '+str(goalTime), 0 )
        self.checkError()
        sleep(0.01)
        self.command( 'SOUR:FALL '+str(goalTime), 0 )
        self.checkError()
        self.cv.release()

    def setRemoteControl(self):
        print( 'setRemoteControl() method called from ' + self.name )
        if self.comStatus == True:
            self.thRemoteCont = Thread( target = self.doSetRemoveControl, name = self.name + '-Remote-Cont', daemon = True )
            self.thRemoteCont.start()
            return True
        else:
            print( self.name, " is not connected; setRemoteControl command not executed" )
            return False
            
    def doSetRemoveControl(self):
        print( 'setRemoteControl() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        if self.comStatus == 1:
            self.command( 'SYST:REM', 0 )
            self.checkError()
        else:
            print( self.name, " is not connected; setRemoteControl command not executed" )
        self.checkError()
        self.cv.release()
    
    
    def setLocalControl(self):
        print( 'setLocalControl() method called from ' + self.name )
        if self.comStatus == True:
            self.thLocalCont = Thread( target = self.doSetLocalControl, name = self.name + '-Local-Cont', daemon = True )
            self.thLocalCont.start()
            return True
        else:
            print( self.name, " is not connected; setLocalControl command not executed" )
            return False
            
    def doSetLocalControl(self):
        print( 'setLocalControl() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        if self.comStatus == 1:
            self.command( 'SYST:LOC', 0 )
            self.checkError()
        else:
            pass
            # print( self.name, " is not connected; setLocalControl command not executed" )
        self.checkError()
        self.cv.release()
        
    def checkError(self):
        if self.comStatus == 1:
            try:
                err = '_'
                err = self.command( 'SYST:ERR?', 1 ).decode()            
                if err[0] == '0':
                    err = '' # no error
                else:
                    print('error detected on ', self.name, '; error code=', err)
            except Exception as error:
                print('err is ', error)
    
    def setTargetVoltage(self, newVoltage=None):
        print( 'setTargetVoltage() method called from ' + self.name )
        ret = True
        try:
            self.targetVoltage = float(newVoltage)
            # print("yeehaw")
        except TypeError: # If none input
            self.targetVoltage = round( 1200/(self.targetCurrent+1e-8), 3 )
        except:
            print("help; newVoltage given was ", newVoltage)
            ret = False
        if self.targetVoltage > 80:
            self.targetVoltage = 80.0
            
        return ret
    
    def setTargetCurrent(self, newCurrent=None):
        print( 'setTargetCurrent() method called from ' + self.name )
        ret = True
        try:
            self.targetCurrent = float(newCurrent)
        except TypeError: # If none input
            self.targetCurrent = round( 1200/(self.targetVoltage+1e-8), 3 )
            # print('targetcurrent is now ', self.targetCurrent)
        except:
            print("help")
            ret = False
        if self.targetCurrent > 60:
            self.targetCurrent = 60.0
            
        return ret
    
    def openFilamentParams(self):
        FilamentParams = None
        try:
            with open(Directory().data + '\\FilamentParams.pkl', 'rb') as file:
                FilamentParams = pickle.load(file)
        except:
            pass
        return FilamentParams
    
    def saveFilamentParams(self, FilamentParams):
        try:
            with open(Directory().data + '\\FilamentParams.pkl', 'wb') as file:
                pickle.dump(FilamentParams, file)
        except:
            pass
        
'''
        # Thermal-model style temp calc
    if self.numFilaments > 0:
        # sigma = 5.670374419e-8 # W/m^2K^4
        # A = 2.83e-4 #m^2 -> surface area of filament
        # Rth = 26.87 # K/W -> thermal resistance from conduction through filament and copper support
    
        Rratio = self.
    
        q = self.power / self.numFilaments # W
        Twall = 300 # K # We don't need the raw number, just T^4
        
        try:
                            
            # temp = np.power( (q/(sigma*0.1*A) + Twallq), 1/4 )
            f = lambda T : abs( -q + sigma*A*0.1*(T**4 - Twall**4) + (T-Twall)/Rth )
            temp = minimize_scalar( f, bounds = (1000, 2150), method='bounded').x
            # print("Small temp is ", temp, " K")
            if temp > 2100:
                f = lambda T : abs( -q + sigma*A*( 0.001*(T-2150)+0.1 )*(T**4 - Twall**4) + (T-Twall)/Rth )
                temp = minimize_scalar( f, bounds = (2100, 2700), method='bounded').x
                # print("Medium temp is ", temp, " K")
                if temp > 2699.8:
                    temp = f = lambda T : abs( -q + sigma*A*0.65*(T**4 - Twall**4) + (T-Twall)/Rth )
                    temp = minimize_scalar( f, bounds = (2700, 3000), method='bounded').x
                    # print("Large Temp is ", temp, " K")
                    
            # print("\nFinal Temp is ", temp, " K.")
            self.temperature = round(temp,-1)# Round to 10s place, since it isn't that accurate anyways
        except:
            print("Error calculating temperature.")
            self.temperature = -1
    return



'''

    
    
# s = BKP9115('Heat #1', 3)
# s.voltage = 2.758
# s.current = 8.615
# s.calcTemp()
# print(s.temperature)
            
# s = BKP9115('Test')
# try:
#     s.connect( 'COM6' )
#     sleep(2)
    
#     # print('v,i: ', s.voltage, ',', s.current )
#     # print('set v,i: ', s.setVoltage,',', s.setCurrent )
#     # print('output? ', s.flgActive)
#     # # s.setTargetVoltage(30)
#     # # s.setTargetCurrent()
#     # s.setOutput(30)
#     # # print('v,i: ', s.voltage, ',', s.current )
#     # # print('set v,i: ', s.setVoltage,',', s.setCurrent )
#     # # print('output? ', s.flgActive)
#     # # # print('v: ', s.targetVoltage, ", i: ", s.targetCurrent)
#     # sleep(0.5)
    
#     # s.enableOutput()
#     # sleep(2)

#     s.pollSystemData()
#     # print('v,i: ', s.voltage, ',', s.current )
#     # print('set v,i: ', s.setVoltage,',', s.setCurrent )
#     # print('output? ', s.flgActive)
#     # sleep(1)
#     # s.disableOutput()
#     # # s.port.write(b'SYST:CLE\r\n')
#     # # s.setRemoteControl()
#     # # sleep(1)
#     # # s.setLocalControl()
    
    
#     # s.command( 'SOUR:RIS 60' )
#     # sleep(0.5)
#     # s.setOutput(10)
#     # sleep(0.5)
#     # s.enableOutput()
    
    
# finally:
#     sleep(2)
#     s.disconnect()