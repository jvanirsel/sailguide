from Basic import PeripheralDevice
from threading import Thread, Condition
from time import sleep
from math import ceil

class Lesker392( PeripheralDevice ):
    def __init__(self):
        super().__init__( 'Lesker 392', 19200, '\r', 2)
        # attributes here
        self.flgActive = False
        self.pressure = 999.
        self.filamentVoltage = 0.0
        self.filamentCurrent = 0.0
        
        
        
    ### Methods ###
    # Overwritten Methods:
    def validateConnection(self):
        print( 'validateConnection() method called from ' + self.name )
        buf = self.command('#01IGS', 13 )
        # print('buf is ', buf, " of length ", len(buf))
        if( buf[0:4] != b'*01 ' or buf[5:9] != b' IG ' ):
            return False
        else:
            return True
        
    def pollSystemData(self):
        self.cv.acquire( ceil(self.timeOut*2.25) )
        # print( 'pollSystemData() method called from ' + self.name )
        ret = False
        buf = self.command( '#01RDS', 13 )
        
        try:
            if len(buf) > 12:
                self.pressure = float( buf[4:12] )
                ret = True
                
            else:
                # self.pressure = 999.9
                print("Error with pressure reading.")
        except:
            print( 'unable to comprehend pressure data ', buf )

        
        if ret == True:
            # print("Trying to poll for IG status..")
            self.doPollIGStatus()
        self.cv.release()
        return ret


    # Unique methods:
    def pollIGStatus(self):
        if self.comStatus == True:
            print( 'pollIGStatus() method called from ' + self.name )
            self.thPollIG = Thread( target = self.doPollIGStatus, name = self.name + '-Poll-IG', daemon = True)
            self.thPollIG.start()
            return True
        else:
            print( self.name, " is not connected; pollIGStatus command not executed" )
            return False
        
    def doPollIGStatus(self):
        buf = self.command( '#01IGS', 13 )
        if len(buf) > 12:
            if buf[4] == '1':
                self.flgActive = 1
            elif buf[4] == '0':
              self.flgActive = -1
            # self.checkPacketCounter( True )
        else:
            self.flgActive = 0
            # self.checkPacketCounter( False )
        

          
    def enableIG(self): # look at if(connected):thing.Do() else: print('bad')
        if self.comStatus == True:
            print( 'enableIG() method called from ' + self.name )
            self.thEnableIG = Thread( target = self.doEnableIG, name = self.name + '-Enable-IG', daemon = True)
            self.thEnableIG.start()
            return True
        else:
            print( self.name, " is not connected; enableIG command not executed" )
            return False
        
    def doEnableIG(self):
        print( 'doEnableIG() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.5) )
        buf = self.command( '#01IG1', 13 ).decode()
        if buf[4:12] == 'PROGM OK':
            print('success') # status update will come from pollIGStatus
        elif buf[0] == '?':
            print("Command not accepted; check IG CNTL on device front panel")
        else:
            # self.flgActive = 0
            print('mistakes were made')
        self.cv.release()
    
    def disableIG(self):
        print( 'DisableIG() method called from ' + self.name )
        if self.comStatus == 1:
            self.thDisableIG = Thread( target = self.doDisableIG, name = self.name + '-Disable-IG', daemon = True)
            self.thDisableIG.start()
            return True
        else:
            print( self.name, " is not connected; disableIG command not executed" )
            return False
    
    def doDisableIG(self):
        print( 'doDisableIG() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.5) )
        buf = self.command( '#01IG0', 13 ).decode()
        print('buf is ', buf)
        if buf[4:12] == 'PROGM OK':
            print('success') # status update will come from pollIGStatus
        elif buf[0] == '?':
            print("Command not accepted; check IG CNTL on device front panel")
        else:
            # self.flgActive = 0
            print('mistakes were made')
        self.cv.release()
    
    def pollFVI(self):
        if self.comStatus == True:
            print( 'readFVI() method called from ' + self.name )
            self.thPollFVI = Thread( target = self.doPollFVI, name = self.name + '-Poll-FVI', daemon = True)
            self.thPollFVI.start()
            return True
        else:
            print( self.name, " is not connected; pollFVI command not executed" )
            return False
        
    def doPollFVI(self):
        print( 'doPollFVI() method called from ' + self.name)
        self.cv.acquire( ceil(self.timeOut*2.25) )
        buf = self.command( '#01RDIGV', 13 ).decode()
        if buf[0] == '*':
            self.filamentVoltage = float( buf[4:11] )
        buf = self.command( '#01RDIGA', 13 ).decode()
        if buf[0] == '*':
            self.filamentCurrent = float( buf[4:11] )
        print(' FVI: ', '{:.1e}'.format(self.filamentVoltage), "V and ", '{:.1e}'.format(self.filamentCurrent), 'A.')
        self.cv.release()
    

# s = Lesker392()
# try:
#     s.connect('COM13')
#     sleep(2)
    
#     # s.pollFVI()
    
#     # print('IG status is ', s.flgActive )
#     # print(" pressure is ", '{:.2e}'.format(s.pressure) )
    
#     # s.pollSystemData()
    
#     # print('IG status is ', s.flgActive )
#     # print(" pressure is ", '{:.2e}'.format(s.pressure) )
    
    
# finally:
#     sleep(2)
#     s.disconnect()