from Basic import PeripheralDevice
from threading import Thread, Condition
from time import sleep 
from struct import unpack
from math import ceil

class MotorController( PeripheralDevice ):
    def __init__(self):
        super().__init__( 'Motor Controller', 115200, '\n', 2)
        # more attributes
        self.z = 0
        self.t = 0
        self.targetZ = 0
        self.targetT = 0
        self.flgActive = 0
        self.offsetZ = 0.0
        self.offsetT = 0.0
        self.minZ = 20
        self.maxZ = 180
        self.minT = -60
        self.maxT = 60

        
    ### Methods ###
    # Overwritten Methods:
    def validateConnection(self):
        print( 'validateConnection() method called from ' + self.name )
        ret = False
        sleep(1)
        buf = self.command( 'I', 9)
        # self.write('I')
        # sleep(1.5)
        # print(self.port.inWaiting(), " bytes in input buffer" )
        # buf = self.port.read(self.port.in_waiting).decode()
        if len(buf) >= 7 and (buf[0] == 6 or buf[0] == 7):
            print('ret = true')
            ret = True
        else:
            print("ret is ", buf, " from validate; len(buf) is ", len(buf))
        # ret = True
        return ret
    
    def pollSystemData(self):
        # print( 'pollSystemData() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        ret = False
        buf = self.command('I', 9 ) # check length
        # print( 'buf[0] is ', buf[0], ' of type ', type(buf[0]) )
        if len(buf) == 9 and (buf[0] == 6 or buf[0] == 7):
            if buf[0] == 6: # if not moving
                self.flgActive = 0
                # print("Moving flag is false")
            elif buf[0] == 7: # if moving
                self.flgActive = 1
                # print("Moving flag is true")
            try:
                self.z = round( unpack( '<f', buf[1:5] )[0], 2 ) - self.offsetZ
                self.t = round( unpack( '<f', buf[5:9] )[0], 2 ) - self.offsetT
                # print(' Z is ', self.z, ' and t is ', self.t )
            except:
                print("MC floating point converstion error")
            
            # print('data back from MC is ', buf)
            ret = True
        elif buf == 21:
            print( "MC returned NAK to status update")
        else:
            print(" unknown MC return from status update; buf = ", buf )
        self.cv.release()
        return ret
        
        
    # Unique Methods
    def move(self, newZ, newT):
        # print( 'move() method called from ' + self.name )
        if self.comStatus == True:
            self.thMove = Thread( target = self.doMove, name = self.name + '-Move', daemon = True, args = (newZ, newT,))
            self.thMove.start()
            return True
        else:
            print( self.name, " is not connected; move command not executed" )
            return False
        
    def doMove(self, newZ, newT):
        # print( 'doMove() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*2.25) )
        if( self.setTargetZ(newZ) ):
            msg = 'Z' + '%.2f' %(self.targetZ+self.offsetZ)
            print("Trying to send message: ", msg)
            
            for i in range(10):
                try:
                    if( not self.command( msg, 1 )[0] == 6 ):
                        print('MC did not acknowledge move Z command. Attempts: ', i)
                    else:
                        print('MC send move command to z=', self.targetZ)
                        break
                except:
                    print('!!!  Error occured in acknowledging move Z command. Attempts: ', i)
                    sleep(0.1)
                    
                    # if( not self.command( msg, 1 )[0] == 6 ):
                    #     print('MC did not acknowledge 2nd move Z command' )
                    # else:
                    #     print('send MC move z successful!')
        if( self.setTargetT(newT) ):
            msg = 'T' + '%.2f' %(self.targetT+self.offsetT)
            print("Trying to send message: ", msg)
            
            for i in range(10):
                try:
                    if( not self.command( msg, 1 )[0] == 6 ):
                        print('MC did not acknowledge move T command. Attempts: ', i)
                    else:
                        print('MC sent move command to θ=', self.targetT, '°')
                        break
                except:
                    print('!!!  Error occured in acknowledging move T command. Attempts: ', i)
                    sleep(0.1)
                
                    # if( not self.command( msg, 1 )[0] == 6 ):
                    #     print('MC did not acknowledge move T command')
                    # else:
                    #     print('send MC move t successful!')
        self.cv.release()
            
        
    def stop(self):
        print( 'cancelMove() method called from ' + self.name )
        if self.comStatus == True:
            self.thStop = Thread( target = self.doStop, name = self.name + '-Stop', daemon = True, args=())
            self.thStop.start()
            return True
        else:
            print( self.name, " is not connected; stop command not executed" )
            return False
        
    def doStop(self):
        print( 'doStop() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        if( not self.command( 'S', 1 )[0] == 6 ):
            print('MC did not acknowledge stop command')
        else:
            print('send MC stop successful!')
        self.cv.release()
        
    def calibrate(self):
        print( 'calibrate() method called from ' + self.name )
        if self.comStatus == True:
            self.thCalibrate = Thread( target = self.doCalibrate, name = self.name + '-Calibrate', daemon = True, args=())
            self.thCalibrate.start()
            return True
        else:
            print( self.name, " is not connected; calibrate command not executed" )
            return False
        
    def doCalibrate(self):
        print( 'doCalibrate() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*1.25) )
        if( not self.command( 'C', 1 )[0] == 6 ):
            print('MC did not acknowledge calibrate command')
        else:
            print('send MC calibrate successful!')
        self.cv.release()
        
        
    def isMoving(self):
        # print( 'isMoving() method called from ' + self.name )
        if self.flgActive == 1:
            return True
        return False
    
    def setTargetZ(self, newZ):
        # print( 'setTargetZ() method called from ' + self.name )
        flag = False

        if type(newZ) is str:
            if len(newZ) == 0:
                return flag
            else:
                try:
                    newZ = float(newZ)
                except:
                    print("unable to convert ", newZ, "to float")
                    
        if type(newZ) is (float or int):
            if newZ > self.minZ and newZ < self.maxZ:
                flag = True
                self.targetZ = round( newZ, 2 )
                # print(" targetZ set to ", newZ )
        else:
            print( 'new Z value ', newZ, " has unknown of type ", type(newZ) )
        return flag
    
    def setTargetT(self, newT):
        # print( 'setTargetT() method called from ' + self.name )
        flag = False
        if type(newT) is str:
            if len(newT) == 0:
                return flag
            else:
                try:
                    newT = float(newT)
                except:
                    print("unable to convert ", newT, "to float")
                    
        if type(newT) is (float or int):
            if newT > self.minT and newT < self.maxT:
                flag = True
                self.targetT = round( newT, 2 )
                # print(" targetT set to ", newT )
        else:
            print( 'new T value ', newT, " is unusable of type ", type(newT) )
        return flag
    '''
    # Implement soon
    def sendCalibration(self, offsetZ, offsetT):
        print( 'sendCalibration() method called from ' + self.name )
        if self.comStatus == True:
            self.thCalibration = Thread( target = self.doSendCalibration, name = self.name + '-Calib', daemon = True, args=(offsetZ,offsetT,))
            self.thCalibration.start()
            return True
        else:
            print( self.name, " is not connected; calibration command not executed" )
            return False
    
    def doSendCalibration(self, offsetZ, offsetT):
        print( 'doSendCalibration() method called from ' + self.name )
        self.cv.acquire( ceil(self.timeOut*2.25) )
        
        msg = 'Z' + '%.2f' %(self.targetZ+self.offsetZ)
        if( not self.command( msg, 1 )[0] == 6 ):
            print('MC did not acknowledge move Z command' )
        else:
            print('send MC move z successful!')
        msg = 'T' + '%.2f' %(self.targetZ+self.offsetT)
        if( not self.command( msg, 1 )[0] == 6 ):
            print('MC did not acknowledge move T command')
        else:
            print('send MC move t successful!')
            
        self.cv.release()
        '''


# s = MotorController()
# try:
#     s.connect( 'COM7' )
#     sleep(3)
    
# #     s.move( 55.5, 33.3 )
# #     sleep(0.3)
# #     s.stop()



# #     # s.pollSystemData()
# #     # sleep(4)
    
# #     # test setters
# #     # print( '    target Z starts as: ', s.targetZ )
# #     # s.setTargetZ( '' )
# #     # print( '    target Z is now: ', s.targetZ )
# #     # s.setTargetZ( 's ')
# #     # print( '    target Z is now: ', s.targetZ )
# #     # s.setTargetZ( 200 )
# #     # print( '    target Z is now: ', s.targetZ )
# #     # s.setTargetZ( 55.5 )
# #     # print( '    target Z is now: ', s.targetZ )
# #     # s.setTargetZ( '65.1')
    
# #     # print( '    target Z starts as: ', s.targetT )
# #     # s.setTargetT( '' )
# #     # print( '    target T is now: ', s.targetT )
# #     # s.setTargetT( 's ')
# #     # print( '    target T is now: ', s.targetT )
# #     # s.setTargetT( 59.999 )
# #     # print( '    target T is now: ', s.targetT )
# #     # s.setTargetT( 3.14156 )
# #     # print( '    target T is now: ', s.targetT )
# #     # s.setTargetT( '-39.32' )
# #     # print( '    target T is now: ', s.targetT )
# finally:
#     sleep(10)
#     s.disconnect()
