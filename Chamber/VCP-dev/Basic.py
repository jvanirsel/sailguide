from serial import Serial
from threading import Thread, Condition
from time import sleep
from VCPThreads import MonitorThread

class SerialDevice():

    def __init__(self, name, baud, eol):
        #Initialize important attributes here
        self.setName(name)
        self.comPort = ''
        self.baudRate = baud
        self.timeOut = 0.5
        self.comStatus = -1
        self.eol = eol
        self.cv = Condition()
        print("Serial Device " + self.name + " is created.")

    def connect(self, newPort):
        print("connect method called from " + self.name)
        self.setComPort( newPort )
        if(self.comPort != '' ):
            self.comStatus = 0.5
            threadName = self.name + "-Connector"
            self.thConnect = Thread(target = self.doConnect, name = threadName, daemon = True)
            self.thConnect.start()
            return True
        else:
            return False

    def doConnect(self):
        print("Connect attempt for " + self.name + " starting")
        if not hasattr(self, 'port'):
            try:
                attempt = 1
                while attempt < 4:
                    self.port = Serial( port = self.comPort, baudrate = self.baudRate, timeout = self.timeOut )
                    if (self.validateConnection()):
                        self.comStatus = 1
                        print("Connected to " + self.comPort + " on " + self.name)
                        return
                    else:
                        self.comStatus = 0.5
                        print("failed attempt " + str(attempt) )
                        attempt = attempt+1
                        sleep(1)
                        del self.port
                print("Failed to connect " + self.name)
                self.comStatus = -1
            except Exception as e:
                print("Error creating serial port for " + self.name)
                print(e)
                self.comStatus = -1
                del self.port
                
    def validateConnection(self):
        print("validateConnection() method called from " + self.name)
        print(" ! ! ! Method has not been defined for this class! ! ! !")
        # To be uniquely overwritten for specific devices.
        return False

    def disconnect(self):
        try:
            if hasattr( self, 'port'):
                del self.port
                self.comStatus = -1
                print(self.name + " disconnected from " + self.comPort)
                self.comPort = ''
                return True
        except:
            print("Error disconnecting ", self.name, " from ", self.comPort)
            return False

    def write(self, message):
        if type(message) is not str:
            try:
                message = str(message)
            except:
                print("Could not convert message to string")
        if hasattr(self, 'port'):
            try:
                txBuf = (message + self.eol).encode()
                self.port.write(txBuf)
                # print(' writing tx buf ', txBuf )
                # print(' EOL is ', self.eol.encode() )
            except TypeError:
                print("Message to " + self.name + " was not in string format")
            except AttributeError as err:
                print('Attribute error: ', err)
            except:
                print("Failed to print message " + message )
        else:
            print("Error-- no port to write to")
            
    def writeByte(self, bite):
        if hasattr(self, 'port'):
            try:
                self.port.write(bite)
            except TypeError:
                print("Message to " + self.name + " was not in string format")
            except AttributeError as err:
                print('Attribute error: ', err)
            except:
                print("Failed to print message " + bite )
        else:
            print("Error-- no port to write to")

    def setName(self, newName):
        if( isinstance(newName, str) ):
            self.name = newName
            print("Serial Device name set to " + self.name)
        else:
            print("Name is not valid string; failed to name Serial Device")
            self.name = 'N/A'

    def setComPort(self, newPort):
        # validate: first 3 letters are COM, after are numbers
        if isinstance(newPort, str):
            if newPort[0:3] == 'COM' and len(newPort) <= 6:
                try:
                    int(newPort[3:])
                    self.comPort = newPort
                    return
                except:
                    print("! Unable to recognize port number of " + newPort)
            else:
                print("! Invalid Com Port '" + newPort + "' on device " + self.name)
        else:
            print("! COM Port was not a string, please help")


class PeripheralDevice( SerialDevice ):
    def __init__(self, name, baud, eol, pollRate):
        super().__init__(name, baud, eol)
        self.pollRate = pollRate
        self.monitor = MonitorThread(self)
        self.badPacketCounter = 0
        
    def disconnect(self):
        self.badPacketCounter = 0 # reset the bad counter
        return super().disconnect()

    def doConnect(self):
        super().doConnect()
        if self.comStatus == 1:
            self.monitor = MonitorThread(self)
            self.startMonitor()
        
    def pollSystemData(self):
        print(self.name + " pollStatus() method is undefined!")

    def startMonitor(self):
        print("startMonitor() method called from " + self.name)
        self.monitor = MonitorThread(self)
        self.monitor.start()
        
    def checkPacketCounter(self, result):
        if result == True:
            self.badPacketCounter = 0
        else:
            self.badPacketCounter = self.badPacketCounter + 1
            print(" !!! - !!! - Bad counter for ", self.name, " at ", self.badPacketCounter )
        
        if self.badPacketCounter > 5:
            self.disconnect()
            
    def command( self, message, returnSize=0 ):
        # print('command() method started')
        try:
            self.port.reset_input_buffer()
            # sleep( 0.01 )
            self.write( message )
            sleep(0.15)
        except:
            print("! unable to send ", message, " to ", self.name)
            
        buf = ''
        # print( self.port.inWaiting(), " bytes in input buffer" )
        if self.name == 'PCS': # It needs a little longer to respond
            sleep(0.5)
        if self.name == 'Motor Controller':
            sleep(0.75)
        try:
            # print("inWaiting is ", self.port.in_waiting, " bytes")
            buf = self.port.read( self.port.in_waiting )
        except:
            print('unable to read' )
        # print('\n message ', message )
        # print(' gets rx buf ', buf, '\n' )
        if( not returnSize == 0 ):
            try:
                if buf[0] == '?':
                    raise ValueError
            except IndexError:
                print( '!!    ' + self.name + ' did not return system data' )
            except ValueError:
                print( '!!    ' + self.name + ' device could not comprehend command ', message )
            else:
                pass
        return buf





#      # Test Suite:
# device = SerialDevice('Device1', 9600)
# print("Connect device test: COM8")
# device.connect( "COM8" )

# sleep(8)
# device.disconnect()
# sleep(1)
# print("Finished tests")