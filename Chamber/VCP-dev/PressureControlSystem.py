from Basic import PeripheralDevice
from threading import Condition, Thread
from VCPThreads import DataRelayThread, MonitorThread
from math import ceil
from time import sleep
from Lesker import Lesker392

class PressureController( PeripheralDevice ):
    def __init__(self, IG):
        super().__init__( 'PCS', 19200, '\r', 2)
        # Attributes here
        self.pressureGauge = IG     # The Lesker 392 object
        self.monitor = MonitorThread(self)
        self.rxMonitor = DataRelayThread(self)
        self.maxPressure = 3e-3
        self.minPressure= 8e-5
        self.setpoint = 0.0
        self.targetSetpoint = 0.0
        self.flgActive = 0
        self.buffer = ''
        self.counter = 0
        
        
    ### Methods ###
    # Overwritten Methods
    def validateConnection(self):
        print( 'validateConnection() method called from ' + self.name )
        ret = False
        buf = self.command('#02IGS\r', 10 ).decode()
        if len(buf) >= 10 and (buf[0:4] == '#01 '):
            ret = True
        return ret
    
    def doConnect(self):
        super().doConnect()
        # if self.comStatus == 1:
            # self.rxMonitor = DataRelayThread(self)
            # self.rxMonitor.start()
            
    
    # Unique Methods
    def pollRx(self):
        # print( 'pollRx() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut) ) 
        bytesAvailable = self.port.in_waiting
        try:
            # print("starting try")
            # print( bytesAvailable, ' bytes available in rx buffer')
            # print( 'sw buffer attr currently reads as ', self.buffer)
            self.buffer = self.buffer + self.port.read(bytesAvailable).decode()
            # print("buffer expanded to read ", self.buffer)
            if self.buffer[-1] == self.eol:
                # print('packet complete,buffer is ', self.buffer)
                if '#01RDS' in self.buffer:
                    self.doTxPressureData()
                    self.buffer = ''
                else:
                    print('incomprehensible return buffer ', self.buffer)
        except IndexError:
            if not len(self.buffer) == 0:
                print("! Unable to index properly in pollRX return")
        except:
            print("! unable to get data in pollRX method")
        self.cv.release()
        if len(self.buffer) > 40:
            print(" PCS Buffer has recieved a lot of undecipherable data: ", self.buffer)
            print(' clearing buffer...')
            self.buffer = ''
    
    def pollSystemData(self):
        # print( 'pollSystemData() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*2.25 ) )
        ret = False
        buf = self.command('#02IGS\r', 10 ).decode()
        # print( 'buf[0] is ', buf[0], ' of type ', type(buf[0]) )
        if len(buf) >= 10 and ('#01 ' in buf):
            try:
                index = buf.index('#01 ')
                self.flgActive = int(buf[ index + 4])
                self.setpoint = int(buf[ index+6:index+9])*1e-6
                ret = True
                # print("PCS status update: active flag reads ", self.flgActive, ", setpoint is ", self.setpoint )
                
                self.counter = (self.counter + 1) % 2
                # print("counter is ", self.counter)
                if self.pressureGauge.comStatus == 1 and self.counter == 0:
                    self.doTxPressureData()
            except:
                print('! unable to parse PCS System data, buf = ', buf)
            # if '#01RDS' in buf: # replace data request message if overwritten
            #     self.buffer = self.buffer + '#01RDS\r'
            #     print(" - re-queued data request")
        elif buf == 21:
            print( "PCS returned NAK to status update")
        else:
            print(" unknown PCS return from status update; buf = ", buf )
        self.cv.release()
        return ret

    def txPressureData(self):
        # print( 'txPressureData() method called from ' + self.name )
        if( self.comStatus == 1 and self.pressureGauge.comStatus == 1):
            self.thTxPressureData = Thread( target = self.doTxPressureData, name = self.name + '-Tx-Data', daemon = True)
            self.thTxPressureData.start()
            return True
        else:
            print( self.name, " is not connected; txPressureData command not executed" )
            return False
        
    def doTxPressureData(self):
        # print( 'doTxPressureData() method called from ' + self.name )
        # self.cv.acquire( ceil(self.timeOut*1.25) ) 
        # if pressure is legitimate
        if self.pressureGauge.pressure != 999 and self.pressureGauge.pressure != 0:
            message = '#02d{:.2e}'.format(self.pressureGauge.pressure)
            if( not self.command( message, 1 )[0] == 6 ):
                print('! PCS did not acknowledge data')
            # else:
                # print('send PCS data send successful!')
        else:
            print('no data to send')
            # self.cv.release()
        
    
    def txSetpoint(self, newSetpoint):
        print( 'applySetpoint() method called from ' + self.name )
        if( self.comStatus == True ):
            self.thTxSetpoint = Thread( target = self.doTxSetpoint, name = self.name + '-Tx-Setpoint', daemon = True, args=(newSetpoint,))
            self.thTxSetpoint.start()
            return True
        else:
            print( self.name, " is not connected; txSetpoint command not executed" )
            return False
        
    def doTxSetpoint(self, newSetpoint):
        print( 'doTxSetpoint() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) ) 
        if( self.setTargetSetpoint(newSetpoint) ):
            message = '#02s{:.2e}'.format(self.targetSetpoint)
            print( 'command sent')
            if( not self.command( message, 1 )[0] == 6 ):
                print('PCS did not acknowledge setpoint')
            else:
                print('send PCS setpoint of', newSetpoint, ' successful!')
        self.cv.release()
        
        
    def enableControl(self):
        print( 'enableControl() method called from ' + self.name )
        if( self.comStatus == True ):
            self.thEnableControl = Thread( target = self.doEnableControl, name = self.name + '-Enable-Control', daemon = True)
            self.thEnableControl.start()
            return True
        else:
            print( self.name, " is not connected; enableControl command not executed" )
            return False
        
    def doEnableControl(self):
        print( 'doEnableControl() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) ) 
        if( not self.command( '#02e', 1 )[0] == 6 ):
            print('! PCS did not acknowledge enableControl command')
        else:
            print('PCS enable control successful!')
        self.cv.release()
        
    def disableControl(self):
        if( self.comStatus == True ):
            print( 'disableControl() method called from ' + self.name )
            self.thDisableControl = Thread( target = self.doDisableControl, name = self.name + '-Disable-Control', daemon = True)
            self.thDisableControl.start()
            return True
        else:
            print( self.name, " is not connected; disableControl command not executed" )
            return False
        
    def doDisableControl(self):
        print( 'doDisableControl() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) ) 
        if( not self.command( '#02z', 1 )[0] == 6 ):
            print('! PCS did not acknowledge disableControl command')
        else:
            print('PCS disable Control successful!')
        self.cv.release()
    
    def setTargetSetpoint(self, newSetpoint):
        print( 'setTargetnewSetpoint() method called from ' + self.name )
        flag = False
        if type(newSetpoint) is str:
            if len(newSetpoint) == 0:
                return flag
            else:
                try:
                    newSetpoint = float(newSetpoint)
                except:
                    print("!! unable to convert ", newSetpoint, "to float")
                    
        if type(newSetpoint) is (float or int):
            if newSetpoint < self.maxPressure:
                flag = True
                self.targetSetpoint = round( newSetpoint, 6 )
            elif newSetpoint == 0:
                self.targetSetpoint = 0
            else:
                print('New setpoint for PCS ', newSetpoint, " is out of bounds <3mTorr")
        else:
            print( '! new Setpoint value ', newSetpoint, " is unusable of type ", type(newSetpoint) )
        return flag
    
    
# ig = Lesker392()
# ig.comStatus = 1
# ig.pressure = 4.52e-4
# s = PressureController(ig)
# try:
#     s.connect('COM16')
#     sleep(4)
    
    
    
# #     # s.rxMonitor.start()
# #     # s.monitor.start()
    
# #     # print( "    Setpoint! -> {:.2e}".format(s.setpoint) )
# #     # s.txSetpoint( 5.12e-4 )
    
# #     # sleep(1)
# #     # print( "    Setpoint! -> {:.2e}".format(s.setpoint) )
    
# #     # s.enableControl()
# #     # sleep(2)
# #     # s.disableControl()
# #     sleep(10)
    
    
    
# finally:
#     sleep(2)
#     print('sleep over, disconnecting...')
#     s.disconnect()