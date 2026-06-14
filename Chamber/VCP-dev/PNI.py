import numpy as np
from Basic import PeripheralDevice
from time import sleep
from threading import Thread

# Add button for take sweep
# check with jonas how i should make take sweep seperate from standard pole

class PNI( PeripheralDevice ):
    def __init__(self):
        super().__init__('PNI',115200,'', 1)
        # data B field
        self.Bx = 0
        self.By = 0
        self.Bz = 0
        self.standard_pole = True
        self.flgActive = -1
        self.NUM = 1 # how many times the PNI will read per each request
    
    # perfect
    def validateConnection(self):
        self.cv.acquire( 1 )
        
        print( 'validateConnection() method called from ' + self.name )
        self.write('m')
        sleep(0.01)
        
        if self.port.read(2) == b'm':
            self.cv.release()
            return True
        self.cv.release()
        return False
    
        

    
    def pollSystemData(self):
        # standard pole sets pni to default mode
        if self.standard_pole:
            self.flgActive = -1
            try:
                data = self.PNIread() # read counts from pni    
            except Exception as e:
               print('error occured in ' + self.name + ' PNIread() - ', e)
               return False
           
            
            try:
                output = self.calibrationPNI_9_30_24(data) # convert counts to uT
            except Exception as e:
                print('error occured in ' + self.name + ' calibrationPNI() - ', e)
                return False
            
            
            try:
                self.update_B(output) # update data
                # print(self.Bx,self.By,self.Bz)
            except Exception as e:
                print('error occured in ' + self.name + ' update_B() - ', e)
                return False
            
            
            return True
        else:
            # currently PNI Poll is unused
            # self.PNIpoll()
            print('PNI Poll is inactive')
            pass
        
    
    def PNIread(self):
        #print("Sending read request ", self.NUM, " times")
        self.cv.acquire( 1 )
        data = np.zeros([self.NUM,3])
        XYZ = np.zeros([self.NUM,9])
        ID = np.zeros([self.NUM,1])
        for index in range(self.NUM):
            out = self.readline_X()
            ctr = 1
            while(len(out) != 10):
                if(ctr > 1):
                    print("WARNING - Readline returned an unexpected number of bytes. Terminator may have appeared in data")
                    print(out);
                out = self.readline_X()
                ctr += 1
            ID[index] = out[0]
            XYZ[index,:] = out[1:10]
            data[index, 0] = self.bytes2int24(out[1],out[2],out[3]) # Output x data
            data[index, 1] = self.bytes2int24(out[4],out[5],out[6]) # Output y data
            data[index, 2] = self.bytes2int24(out[7],out[8],out[9]) # Output z data
            
        self.cv.release()

            # -----------
            #print(ID)
            #print(XYZ)
            # print(data)
        
        return data #, XYZ, ID
    
    # unused currently
    def PNIpoll(self):
        if self.comStatus == True:
            print( 'PNIpoll() method called from ' + self.name )
            self.thPollPNI = Thread( target = self.doPNIpoll, name = self.name + '-Poll-PNI', daemon = True)
            self.thPollPNI.start()
            return True
        else:
            print( self.name, " is not connected; doPNIpoll command not executed" )
            return False
    
    def doPNIpoll(self):
        print("PNI poll does nothing")
        
    # read line up until 'X' char
    def readline_X(self):
       self.write('l')  # write character to PNI telling PNI to send PNI data back
       sleep(0.1)
       waiting = self.port.read( self.port.in_waiting ) # read characters from PNI
       end = waiting.index(b'X') # cutoff data at cutoff bit
       arr = waiting[0:end]
       out = [arr[0]] # initialize output first bit expected to be bit sent
       # apend ints from bytes onto out
       for i in range(1,len(arr)):
           bit = arr[i]
           # print("Bit is ", bit, " of type ", type(bit))
           if type(bit)==bytes:
               out.append( int.from_bytes(bit, 'big') ) 
           else:
               out.append(bit)
       # print(out)
       
       return out

    def bytes2int24(self, int_byte1, int_byte2, int_byte3):
        byte1 = np.uint32((int_byte1))
        byte2 = np.uint32((int_byte2))
        byte3 = np.uint32((int_byte3))
        
        msb = format(byte1,'#010b')[2]
        mx = 2**23*(msb=='1')
        B1 = ((byte1&0x7F)<<16 | byte2<<8 | byte3)
        out = B1 - mx
        
        return out
    
    def update_B(self, output):
        self.Bx = round(output[0].item(), 2) #.item() to read as scalar, not 1x1 array
        self.By = round(output[1].item(), 2)
        self.Bz = round(output[2].item(), 2)
    
    def calibrationPNI_9_30_24(self, data):
        # convert counts to uT
        gain = np.asarray([[0.001371,-5e-5,-3.9e-5],[3.22e-5,0.001388,0.000138],[6.3e-5,-0.00015,0.001465]]) # units (uT/count)
        output = np.matmul(gain,data.T)
        #print('output - ', output)
        return output
    
    
        
        