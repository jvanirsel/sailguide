import numpy as np
from time import sleep
from Basic import SerialDevice
from misc import Directory
import scipy as sc
import scipy.io as sio
from scipy.signal import savgol_filter
from threading import Thread, Condition
from math import ceil, floor, log
import datetime as dt
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import warnings

class WSLP( SerialDevice ):
    def __init__( self ):
        super().__init__('WSLP', 3000000, '')
        self.flgActive = 0
        self.version = '2.1'
        self.sweepLeg = []
        self.sweepProfile = np.array([])
        self.dwellSide = 'ion'
        # self.dirManager = ()
        self.filepath = Directory().data
        self.filename = 'n/a'
        self.Ge = {}
        self.E = {}
        
        # These change from Version to version
        if self.version == '2.1':
            self.maxCount = 65535
            self.minCount = 4250
            self.headerData = {'boardID':1}
        elif self.version == '2.2':
            self.maxCount = 61835 
            self.minCount = 3600
            self.headerData = {'boardID':2}
        # More attributes
        self.newData = 0
        self.ch1 = np.array([])
        self.ch2 = np.array([])
        self.header = self.headerData
        
    # Unique Methods
    def doConnect(self):
        super().doConnect()
        if self.comStatus==True:
            # Need to extend rx buffer to allow for large sweep data dumps
            self.port.set_buffer_size(rx_size = 550000) 
            
    def connect(self, newPort):
        self.baudRate = 2000000
        print("Attempting WSLP connection with 2MBaud rate")
        super().connect(newPort)
        count = 0
        while self.comStatus == 0.5 or count < 10:
            if self.comStatus == 1:
                self.newData = 1
                break
            # print("WSLP com status still at ", self.comStatus, ", waiting at count ", count, "/10")
            sleep(0.5)
            count = count+1
        if self.comStatus == -1:
            print("trying 3MBaud rate...")
            self.baudrate = 3000000
            super().connect(newPort)
        
        
    def validateConnection(self):
        print( 'validateConnection() method called from ' + self.name )
        ret = False
        try:
            self.port.reset_input_buffer()
            self.write( '\x07' )
            # print(" !ding")
            sleep(0.25)
        except:
            print("! unable to send BEL to ", self.name)
        try:
            if self.port.in_waiting > 0:
                # print("Buf? What buf?")
                buf = self.port.read( self.port.in_waiting )
                # print("Oh you mean this buf?", buf)
                if buf[0:5] == b'W_SLP':
                    self.parseHeader(buf)
                    ret = True
                else:
                    print("Unknown buf return, ", buf)
                    print("First 5 of buf: ", buf[0:5])
            else:
                print("No buffer to collect?")
                    
        except IndexError:
            print( '!!    ' + self.name + ' did not return system data' )
        except ValueError:
            print("Buf is {:x}".format(buf))
        except Exception as err:
            print("Unknown Error of type ", type(err), ": ", err)
        
        return ret
        
    def generateSweepLeg(self, numSteps):
        self.sweepLeg = np.linspace(self.maxCount, self.minCount, num=numSteps, dtype = float)
        self.sweepLeg = np.uint16(self.sweepLeg)
        
        if self.dwellSide =='electron':
            self.sweepLeg = np.flip(self.sweepLeg)
        
    def generateSweepProfile(self, numSweeps, numSteps, numDwells ):
        print("generateProfile() method called from WSLP")
        self.generateSweepLeg(numSteps)
        
        if self.dwellSide == 'ion':
            dwell = np.fromiter( (self.minCount for a in range(numDwells)), int )
        else:
            dwell = np.fromiter( (self.maxCount for a in range(numDwells)), int )
            
        sweeps = np.array([])
        for i in range(numSweeps):
            sweeps = np.append( sweeps, np.append( np.flip(self.sweepLeg), self.sweepLeg, axis=0), axis=0 )
        # Assemble
        self.sweepProfile = np.append( dwell, np.append(sweeps, dwell, axis=0 ), axis=0)
        # print("Full profile is ")
        # print(self.sweepProfile)
        
    
    def programSweep( self, numSweeps, numSteps, numDwellsOrGroups, numSamples ):
        if(self.comStatus == 1):
            self.thProgramSweep = Thread( target = self.doProgramSweep, name = self.name + '-Program-Sweep', daemon = True, args=(numSweeps, numSteps, numDwellsOrGroups, numSamples,))
            self.thProgramSweep.start()
            return True
        else:
            print( self.name, " is not connected; programSweep command not executed" )
            return False
        
    def doProgramSweep(self, numSweeps, numSteps, numDwellsOrGroups, numSamples ):
        self.cv.acquire( round(self.timeOut*4) )
        print( 'programSweep() method called from ' + self.name )
        print("NumSweeps = ", numSweeps, ", numSteps = ", numSteps, ", numDwells/Groups = ", numDwellsOrGroups, ", numSamples = ", numSamples)
        if self.version == '2.1':
            print("Overwritten: we don't have dwell capability")
            numDwellsOrGroups = 0
            print("NumSweeps = ", numSweeps, ", numSteps = ", numSteps, ", numDwells = ", numDwellsOrGroups, ", numSamples = ", numSamples)
        SOH = '\x01'
        STX = '\x02'
        ETX = '\x03'
        EOT = '\x04'
        SS = '\x0F' # Swap to sweep mode
        
        self.generateSweepProfile( numSweeps, numSteps, numDwellsOrGroups )
        
        # Do the Thing
        successFlag = False
        if not self.cmdByte(SS):
            print("Error getting WSLP ready for sweeps. Aborted sweep programming")
            return
        if self.cmdByte( SOH ):
            # print("SOH")
            self.writeByte( bytes([numSteps >> 8]) ) 
            self.writeByte( bytes([numSteps & 0xFF]) )
            self.writeByte( bytes([numSweeps>>8]) )
            self.writeByte( bytes([numSweeps & 0xFF]) )
            self.writeByte( bytes([numDwellsOrGroups]) )
            self.writeByte( bytes([numSamples]) )
            if self.cmdByte( STX ):
                # print("STX")
                # Slice up data
                buffer = []
                for i in range(0,numSteps):
                    buffer.append(self.sweepLeg[i]>>8)
                    buffer.append( self.sweepLeg[i] & 0x00FF)
                    
                for byte in buffer:
                    self.writeByte( bytes([byte]) )
                    
                if self.cmdByte( ETX ):
                    # print("ETX")
                    if self.cmdByte( EOT ):
                        successFlag = True
        
        if successFlag == True:
            print("WSLP Programmed successfully")
            self.validateConnection()
            self.newData = 1
        else:
            print("WSLP programming failed :(")
        self.cv.release()
        return
        
    def parseHeader(self, data):
        boardID = int(data[5])
        
        if boardID == 1:
            self.version = '2.1'
            self.maxCount = 65535
            self.minCount = 4250
                
            headerData = {
                "boardID" : int(data[5]),
                "biasState" : int(data[6]),
                 # Timer duration: N/A for WSLP, so data[8] is num dwells
                "numDwells" : int(data[8]),
                "numSweeps" : int( np.uint16(data[9])<<8 | np.uint16(data[10]) ),
                "numSteps" : int( np.uint16(data[11])<<8 | np.uint16(data[12]) ),
                "numSamples" : int(data[13]),
                "maxDAC" : np.uint16(data[14])<<8 | np.uint16(data[15]),
                "minDAC" : np.uint16(data[16])<<8 | np.uint16(data[17]),
                "feedbackR" : int(np.uint16(data[18])<<4 | np.uint16(data[19])>>4)  * 10**int(( np.uint8(data[19]) & 0x0F )),
                "Ch1Gain" : data[20],
                "Ch2Gain" : data[21],
                "resHK" : data[22],
                "chHK" : data[23]
                }
            print("Board version 2.1")
            self.generateSweepProfile(headerData['numSweeps'], headerData['numSteps'], headerData['numDwells'] )
            self.headerData = headerData
            return headerData
        
        elif boardID == 2:
            sweepDir = int(data[6])
            if sweepDir == 0:
                sweepDir = 'Down'
            elif sweepDir == 1:
                sweepDir = 'Up'
            elif sweepDir == 2:
                sweepDir = 'Hold'
            else: 
                print("unknown sweepDir: ", sweepDir)
                
            headerData = {
                "boardID" : int(data[5]),
                "sweepDirection" : sweepDir,
                "sweepIndex" : int( data[7] ),
                "numGroups" : int( data[8] ),
                "numSweeps" : int( np.uint16(data[9])<<8 | np.uint16(data[10]) ),
                "numSteps" : int( np.uint16(data[11])<<8 | np.uint16(data[12]) ),
                "numSamples" : int(data[13]),
                "DACstart" : np.uint16(data[14])<<8 | np.uint16(data[15]),
                "DACstop" : np.uint16(data[16])<<8 | np.uint16(data[17]),
                "feedbackR" : int(np.uint16(data[18])<<4 | np.uint16(data[19])>>4)  * 10**int(( np.uint8(data[19]) & 0x0F )),
                "Ch1Gain" : data[20],
                "Ch2Gain" : data[21],
                "resHK" : data[22],
                "chHK" : data[23]
            }
            try:
                # print( "header is ", headerData)
                headerData['estFreq'] = 20000/(2*headerData['numSamples'] * headerData['numSteps'])
            except:
                pass
            self.headerData = headerData
            self.version = '2.2'
            self.maxCount = 61835 
            self.minCount = 3600
            # print("Board version 2.2")
            
            return headerData
        else: 
            print("Unknown board ID")
        
        

    def takeSweep(self, saveFlag, systemData):
        if(self.comStatus == 1):
            self.thTakeSweep = Thread( target = self.doTakeSweep, name = self.name + '-Take-Sweep', daemon = True, args=(saveFlag,systemData,) )
            self.thTakeSweep.start()
            return True
        else:
            print( self.name, " is not connected; programSweep command not executed" )
            return False
    
    def doTakeSweep(self, saveFlag, systemData):
        # self.startT = time.time()
        if not self.validateConnection():
            print("WSLP not connected. Aborting sweep")
        else:
            self.flgActive = 1
            ENQ = '\x05'
            
            # Guess how long it should take
            try:
                timePerStep = 50e-6 # 33.3333 µs actually, for Fs = 30kHz; 50µs for 20kHz
                numTotalSteps = (self.headerData['numSteps'])*self.headerData['numSamples']*(2*((self.headerData['numSweeps']+1)*(self.headerData['numGroups']-1)+self.headerData['numSweeps']))
                t = timePerStep * numTotalSteps + 2 # add 2 seconds of margin, just in case
                # print("Expecting ", numTotalSteps, " steps from ", self.headerData['numSweeps'], "sweeps per ", self.headerData['numGroups'], " groups" )
                # print("Total time should be <", t, " seconds")
            except:
                print("Couldn't calc time, using 20 seconds")
                t = 20
            numAttempts = 4
            self.cv.acquire( int(numAttempts*t) )
            for i in range(numAttempts):
                # print("Attempting sweep, try", i+1,'/',numAttempts)
                if self.cmdByte( ENQ ):
                    # print('Sweep Commanded: total elapsed time is %.3f seconds' % (time.time() - self.startT))
                    # print("Sweep started!")
                    pass
                else:
                    continue
                sleep(t) # Wait for bytes to come in.
                try:
                    # print('Starting read: total elapsed time is %.3f seconds' % (time.time() - self.startT))
                    buf = self.port.read(self.port.in_waiting)
                    # print("Sweep completed! ", len(buf), " bytes taken, only ", self.port.in_waiting, " bytes left in buffer")
                    # print('Finished read: total elapsed time is %.3f seconds' % (time.time() - self.startT))
                    if self.version == '2.1':
                        self.parseSamplesV1( buf )
                    elif self.version == '2.2':
                        self.parseSamplesV2( buf )
                    break
                except Exception as err:
                    print("Problem collecting data. Aborting...")
                    print(f"Unexpected {err=}, {type(err)=}")
                
            # print("saveflag is ", saveFlag)
            try:
                if saveFlag == True:
                    # print("saving as ", self.filename)
                    self.saveSweep(systemData)
                
                # print( "Finished sweep protocol." )
                self.flgActive = 0
                self.newData = 1
                result = True
            except:
                print("Unable to finish sweep")
                result = False
            self.cv.release()
            return result
    
    def parseSamplesV2( self, rawData ):
        # print("parseSamplesV2")
        self.spacer = np.array([ 0x57, 0x5F, 0x53, 0x4C, 0x50 ], dtype=np.uint8)
        constBytes = 24
        data = np.asarray( bytearray(rawData), dtype=np.uint8 )
        self.rawData = data
        boolI = np.all(self.findHeader(data, len(self.spacer))==self.spacer, axis=1)
        I = np.mgrid[0:len(boolI)][boolI]
        
        firstPacketInd = I[0]
        lastPacketInd = I[-1]
        
        # Extract Header Info
        header = data[firstPacketInd:(firstPacketInd+constBytes) ]
        header1 = self.parseHeader( header )
        self.h = header1
        CH = 2
        dataSize = 3*CH*header1['numSteps'] + constBytes # For counting Bytes
        sweepSize = header1['numSteps'] # For counting samples for re-shaping later
        
        if( len(rawData) == lastPacketInd+dataSize ):
            lastPacketInd = len(rawData)
            I = np.append(I, lastPacketInd)
            ## Check this. Probably not right
            
        dI = np.diff(I)
        if len(dI) == 0:
            print("!! No Good data to parse !!")
            return
        I2 = [I[i] for i in [i for i,v in enumerate(dI) if v==dataSize] ]
        numGoodSweeps = len(I2)

        # Parse headers
        headers = {}
        for ct in range(numGoodSweeps):
            headers["Sweep_"+str(ct)] = self.parseHeader( data[I2[ct]:I2[ct]+constBytes] )
            
        self.header= headers
        
        # print("\nSuccesfully retrieved ", numGoodSweeps, "/", 2*((header1['numSweeps']+1)*(header1['numGroups']-1)+header1['numSweeps']), " sweep legs\n")
        
        
        trimmedData = np.array([])
        for ct in range(numGoodSweeps):
            trimmedData = np.append( trimmedData, data[I2[ct]+constBytes:I2[ct]+dataSize], axis=0 )
        # Convert to counts
        trimmedData = np.reshape(trimmedData, [-1,3] ).astype(np.uint32)
        self.trimmedData = trimmedData
        rawCounts = self.convertToCounts20(trimmedData)
        self.counts = np.reshape(rawCounts, (-1,2) ) # Splits to high gain, and unity channels
        
        # Scaling correction for irregular number of ADC samples (non powers of 2)
        self.ct1 = np.atleast_2d(self.counts[:,1]).T * 2**(ceil( log(self.h['numSamples'])/log(2)) )/self.h['numSamples'] # Unity
        self.ct2 = np.atleast_2d(self.counts[:,0]).T * 2**(ceil( log(self.h['numSamples'])/log(2)) )/self.h['numSamples'] # High Gain
        dac = np.array([])
        for ct in range(numGoodSweeps):
            name = "Sweep_"+str(ct)
            dacLeg  = np.linspace(headers[name]['DACstop'], headers[name]['DACstart'], num=headers[name]['numSteps'], dtype = int)
            dac = np.append(dac, dacLeg)
        self.dac = np.atleast_2d(dac).T
        
        self.applyV2Calibration()
        
        # Calculate Vps, EEDF
        self.E = {}
        self.Ge = {}
        for k in range( (np.size(self.ch1, axis=2))):
            try:
                # Make Estimations
                Vp = self.estimateVp(self.ch1[:,:,k])
                Te, Ne, E, Ge = self.estimateEEDF(self.ch1[:,:,k])
                
                # Store
                # print("K = ", k)
                # print(" Attempting save for Vp = ", Vp, ", Ne = ", Ne, ", Te = ", Te)
                self.header["Sweep_"+str(k)]['estVp'] = Vp
                # print("V")
                self.header["Sweep_"+str(k)]['estNe'] = Ne
                # print("N")
                self.header["Sweep_"+str(k)]['estTeeV'] = Te
                # print("T")
                
                self.E["Sweep_"+str(k)] = E
                self.Ge["Sweep_"+str(k)] = Ge
                
            except:
                print("Error in estimations (!)")
            
    def estimateVp(self, ch):
        try:
            I = ch[:,3]
            V = ch[:,2]
            
            ch[0,3] = ch[1,3]
            if abs(max(ch[:,3])-min(ch[:,3])) < 2e-6: # if minimal signal, don't try
                # print("skip 1")
                return 0
            dI = savgol_filter( np.gradient(I, V), 11, 1)
            if V[0] > V[-1]:
                # print("should have flipped")
                dI = np.flip( dI )
                V = np.flip( V )
            if ( np.abs( V[0] + V[-1] ) > 1):
                # print("skipping held(?) leg")
                Vp = 0
                return Vp
            ind = np.argmax( np.abs(dI[(V<20)]) )
            Vp = V[ind]
        except:
            print("Error estimating Vp")
            Vp = 0
            
        return Vp
        
    def estimateEEDF(self, ch):
        # Assume HSLP Mk 2
        Te = 0
        Ne = 0
        A = 45e-3 * 5.6e-3 * np.pi
        qe = 1.602e-19
        me = 9.1094e-31
        # mi = 1.6726e-24
        # kB = 1.381e-23
        Ge = []
        E = []
        if abs(max(ch[:,3])-min(ch[:,3])) < 2e-6: # if minimal signal, don't try
            return Te, Ne, E, Ge
        try:
            V = ch[:,2]
            I = ch[:,3]
            self.I, self.V = I, V
            if V[0] > V[-1]: # flip upside down data
                V = np.flipud(V)
                I = np.flipud(I)
                # print("Flipped")
            # print(" V[0] = ", ch[0,2], ', and V[-1] = ', ch[-1,2] ) 
            
            dI = np.gradient(I, V)
            dI = savgol_filter( dI, 11, 1)
            dI2 = savgol_filter( np.gradient(dI, V), 7, 1)
            ind = np.argmax( np.abs(dI[(V<20)]) )
            # Vp = V[ind] # Vp is unused?
            
            Vge = np.flipud( V[0:ind] )
            E = np.abs(Vge-V[ind])
            Ge = (me*2)/(qe**2 * A)*np.sqrt( (2*qe/me) * E ) * np.flipud(dI2[0:ind])
            
            points = 100
            epsilon = E[0:points]
            Ge_crop = (Ge[0:points])
            Ne = np.trapezoid( Ge_crop, x=epsilon ) 
            # print("Ne = {:.1e}".format(Ne) )
            
            Eavg = 1/Ne * np.trapezoid( epsilon*Ge_crop, x=epsilon )
            Te = 2/3*Eavg
            # print("Te = {:.1f}eV".format(Te) )
        
        except:
            print("Error estimating EEDF, rip")
        return Te, Ne, E, Ge
    
    
    def applyV2Calibration(self):
        # print("applyV2Calibration() method called")
        try:
            name = Directory().data + '\\' + "WSLP_V2_CALIB_COEF2.mat"
            coefs = sio.loadmat(name)
        except:
            print("error opening calibration coefficients file")
            return
        voltageCoefs = coefs['Vc_u']
        
        unityCounts = coefs['lg_ct_coef']
        unityCurrent = coefs['lg_I_coef']
        unityIest, ind = np.unique( np.squeeze(coefs['lg_I_est']), return_index = True )
        unityIres = np.squeeze(coefs['lg_I_residual'])[ind]
        
        highIest, ind = np.unique( np.squeeze(coefs['hg_I_est']), return_index = True )
        highIres = np.squeeze(coefs['hg_I_residual'])[ind]
        highCounts = coefs['hg_ct_coef']
        highCurrent = coefs['hg_I_coef']

        # Volts calibration
        Xu = np.asarray( [np.ones( (len(self.ct1),1) ), self.dac, self.ct1] ).T
        self.V = np.atleast_2d( np.squeeze(np.matmul(Xu, voltageCoefs)) ).T
        
        # Unity Gain cal
        adc = (self.ct1 - np.matmul(np.squeeze(np.asarray( [np.ones((len(self.ct1),1)), self.dac, self.dac**2] )).T, unityCounts) ) / (2**20)
        self.adc = adc
        I_temp = 1e6*np.matmul( np.squeeze(np.asarray([np.ones((len(adc),1)), adc])).T, unityCurrent) 
        self.I_temp = I_temp
        
        spl = sc.interpolate.make_smoothing_spline( unityIest, unityIres, lam = 1000)
        I_est = spl(I_temp)
        Iu = I_temp-I_est
        self.Iu = Iu * 1e-6
        
        # High Gain cal
        adc = (self.ct2 - np.matmul(np.squeeze(np.asarray( [np.ones((len(self.ct2),1)), self.dac, self.dac**2] )).T, highCounts) ) / 2**20
        I_temp = 1e6*np.matmul( np.squeeze(np.asarray([np.ones((len(adc),1)), adc])).T, highCurrent) 
        spl = sc.interpolate.make_smoothing_spline( highIest, highIres, lam = 1000)
        I_est = spl(I_temp)
        Ih = I_temp-I_est
        self.Ih = Ih * 1e-6
        
        # end: assemble channel datasets
        ch1 = np.asarray( [self.dac, self.ct1, self.V, self.Iu] ).transpose(1,0,2)
        self.ch1 = np.rollaxis( np.reshape( np.rollaxis( np.atleast_3d(ch1), 2, 0 ), (-1, self.h['numSteps'], 4) ), 0, 3 )
        ch2 = np.asarray( [self.dac, self.ct2, self.V, self.Ih] ).transpose(1,0,2)
        self.ch2 = np.rollaxis( np.reshape( np.rollaxis( np.atleast_3d(ch2), 2, 0 ), (-1, self.h['numSteps'], 4) ), 0, 3 )
    
        
 
    def saveSweep(self, systemData):
        # print("saveSweep() method called from WSLP")
        try:
            # sc.io.savemat( self.filename)
            # print("Directory path is ", self.filepath)
            # print("filename is ", self.filename)
            name = self.filepath + '\\' +self.filename
            # print("so total is ", name)
            time = dt.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if systemData:
                systemData['Time'] = time
            
            count = 1
            tempName = name
            while os.path.isfile(tempName):
                count = count+1
                tempName = name[0:-4] + '_' + str(count) + '.mat'
                if count > 10:
                    print("Too many (>10) files with same name; overwriting file as ", tempName)
                    break
            
            print("saving file as ", tempName)
            # print("\n\nrawData has size ", np.size(self.rawData) ) 
            sio.savemat(tempName, {'sweepData':self.header, 'systemData':systemData, 'lg':self.ch1, 'hg':self.ch2, 'rawData':self.rawData })
            
        except Exception as err:
            print("Problem collecting data; not saved :(")
            print(f"Unexpected {err=}, {type(err)=}")
        
    def setFileName(self, prefix, suffix, data, status ):
        # print("setFileName() method called from WSLP")
        # print( "Prefix is ", prefix, ", suffix is ", suffix)
        # print("data is ", data)
        filename = ''
        # Assemble filename in the following order:
        # [prefix]__[pressure]Torr_[Vbias]V-[Ibias]bias_[Avg temp]_[Z]z_[±T]t__[suffix]
        # If a peripheral is unconnected, then skip that section
        try:
            if prefix != '':
                filename = filename + prefix + '__'
            if status['l392'] == 1:
                # p = '{:.0f}uTorr'.format(data['Pressure'])
                filename = filename + '{:.0f}uTorr'.format(data['Pressure']*1e6) #p[0:-2]+p[-1]+'Torr'
            if status['bias'] == 1:
                a = '{:.1f}'.format(data['Bias, A'])
                filename = filename + '_{:.0f}'.format(data['Bias, V']) + '-' + a[0:-2]+'A'+a[-1]+'Bias'
            if status['heat1'] == 1 or status['heat2'] == 1:
                if status['heat1'] == 1 and status['heat2'] == 0:
                    temp = data['Heat1, T']
                if status['heat2'] == 0 and status['heat2'] == 1:
                    temp = data['Heat1, T']
                if status['heat1'] == 1 and status['heat2'] == 1:
                    temp = (data['Heat1, T']+data['Heat2, T'])/2
                filename = filename + '_{:.0f}K-Heat'.format(temp)
            if status['mc'] == 1:
                z = '{:.0f}z'.format(data['Motor Z'])
                t = '_{:.0f}t'.format(data['Motor T'])
                filename = filename + '_' + z + t
            if suffix != '':
                filename = filename + '__' + suffix
            
            if len(filename) == 0:
                filename = 'n/a'
            else:
                filename = filename + '.mat'
            
            # print("Filename is ", filename)
            self.filename = filename
        except TypeError:
            print("Something was the wrong type for ")
        except:
            print("Error setting filename")
    
    def resetDirectory(self):
        print("resetDirectory() method called from WSLP")
        self.filepath = Directory().data
    
    # Misc functions
    def cmdByte( self, message ):
        # print('command() method started')
        try:
            self.port.reset_input_buffer()
            sleep( 0.1 )
            self.write( message )
            sleep(0.15)
        except:
            print("! unable to send ", message, " to ", self.name)
            
        ret = False
        buf = []
        try:
            if self.port.in_waiting > 0:
                buf = self.port.read( 1 ).decode()
            if buf[0] == '\x15':
                print("NAK")
            elif buf[0] == '\x06':
                ret = True
        except IndexError:
            print( '!!    ' + self.name + ' did not return system data' )
        except ValueError:
            print( '!!    ' + self.name + ' device could not comprehend command ', message )
            print("Buf is {:x}".format(buf))
            ret = False
        return ret
    
    def findHeader(self, a, size):
     shape = a.shape[:-1] + (a.shape[-1] - size + 1, size)
     strides = a.strides + (a. strides[-1],)
     # print(shape)
     # print(strides)
     return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
 
    def movmean(self, data, window_size):
        window = np.ones(window_size) / window_size
        return np.convolve(data, window, mode='valid')
 
    def convertToCounts20(self, data): # For 20-bit numbers
        out = np.zeros((np.size(data,0),1), dtype=np.int32)
        for ct in range(np.size(data,0)):
            msb = format(int(data[ct,0]), '#010b')[2]
            mx = ((1<<19)*(msb=='1'))
            B1 = ((data[ct,0]&127)<<12) | (data[ct,1]<<4) | (data[ct,2]>>4)
            out[ct] = (int(B1) - int(mx))
            # if ct == 0:
            #     print("mx= ", mx, ", data is (", data[ct,0],",",data[ct,1],',',data[ct,2],')')
            #     print("B1: ", B1, ", out&0xFFF: ", (out[ct]))
        return out
    
    def convertToCounts24(self, data): # For 24-bit numbers
        out = np.zeros((np.size(data,0),1))
        for ct in range(np.size(data,0)):
            msb = format(int(data[ct,0]), '#010b')[2]
            mx = (1<<23)*(msb=='1')
            B1 = np.uint32((data[ct,0]&127)<<16) | (data[ct,1]<<8) | (data[ct,2])
            out[ct] = B1 - mx
        return out
        
    
    #######################################################################################################

    #######################################################################################################

    #######################################################################################################
    
    #######################################################################################################
    
    #######################################################################################################
    # old
    def parseSamplesV1(self, rawData):
        self.spacer = np.array([ 0x57, 0x5F, 0x53, 0x4C, 0x50 ], dtype=np.uint8)
        constBytes = 24
        
        data = np.array([])
        for byte in rawData:
            data = np.append( data, np.uint8(byte) )
        
        boolI = np.all(self.findHeader(data, len(self.spacer))==self.spacer, axis=1)
        I = np.mgrid[0:len(boolI)][boolI]
        # print(data[0:30])
        # print(I)
        
        firstPacketInd = I[0]
        lastPacketInd = I[-1]
        
        
        # Extract Header Info
        header = data[firstPacketInd:(firstPacketInd+24) ]
        # print(header)
        self.h = self.parseHeader( header )
        CH = 2
        dataSize = 6*CH*self.headerData['numSteps'] + constBytes # For counting Bytes
        sweepSize = 2*self.headerData['numSteps'] # For counting samples for re-shaping later
        
        # In case full last packet is not terminated with another header
        if( len(rawData) == lastPacketInd+dataSize-1 ):
            lastPacketInd = len(rawData)-1
            I = np.append(I, lastPacketInd+1)
            ## Check this. Probably not right
            
        dI = np.diff(I)
        if len(dI) == 0:
            print("!! No Good data to parse !!")
            return
        #I2 = I(matlab.find()dI=dataSize)
        I2 = [I[i] for i in [i for i,v in enumerate(dI) if v==dataSize] ]
        numGoodSweeps = len(I2)
        
        print("\nSuccesfully retrieved ", numGoodSweeps, "/", self.headerData['numSweeps'], " sweeps\n")
                
        
        #Split up good sweeps and trim headers off. Cat to one array
        trimmedData = np.array([])
        for ct in range(numGoodSweeps):
            trimmedData = np.append( trimmedData, data[I2[ct]+constBytes:I2[ct]+dataSize], axis=0 )
        
        # Convert to counts
        trimmedData = np.reshape(trimmedData, [-1,3] ).astype(np.uint32)
        if self.version == '2.1':
            rawCounts = self.convertToCounts20(trimmedData)
        if self.version > '2.1':
            rawCounts = self.convertToCounts20(trimmedData)
        
        self.counts = np.reshape(rawCounts, (-1,2) )
        dac = np.append( np.flip(self.sweepLeg), self.sweepLeg, axis = 0)
        self.dacCounts = np.repeat( np.atleast_2d(dac), self.headerData['numSweeps'], axis=0 ).flatten()
        
        if self.version == '2.1':
            self.applyV1Calibration(numGoodSweeps)
        elif self.version == '2.2':
            self.applyV2Calibration()
        
        
        print("Finished parsing data")
        
        
    
            
    
    def applyV1Calibration(self, numGoodSweeps):
        # print("applyV1Calibration() method called")
        fit_coef = np.array( [[-40.0589772931786, 0.00113059104680074], [-291538.265020877,0.00112896526431047],[-7120.18661670979,0.112645785620053]]  )
        calib_coef = np.array( [[1.46600914890588e-07, 3.05154012782975e-10],[1.86107422066320e-10, 3.05182872532763e-12]] )
            
            #[[5.17107049371732e-08, 1.35672514332706e-09],[ 4.81452902426490e-09, 1.35841428965173e-11]] )
            
            # [[1.46600914890588e-07, 3.05154012782975e-10],[1.86107422066320e-10, 3.05182872532763e-12]])
        offset_I1 = 14.5e-8
        offset_I2 = 0
        
        volts = (fit_coef[0,1]*self.dacCounts + fit_coef[0,0])
        
        temp1 = self.counts[:,1] - (fit_coef[1,1] * self.dacCounts + fit_coef[1,0])
        temp2 = self.counts[:,0] - (fit_coef[2,1] * self.dacCounts + fit_coef[2,0])
        
        I1 = calib_coef[0,1]* temp1 + calib_coef[0,0] - offset_I1
        I2 = calib_coef[1,1]* temp2 + calib_coef[1,0] - offset_I2
        
        ch1 = np.append( np.atleast_2d(self.counts[:,1]), np.append(np.atleast_2d(volts), np.atleast_2d(I1), axis=0), axis=0).T
        ch2 = np.append( np.atleast_2d(self.counts[:,0]), np.append(np.atleast_2d(volts), np.atleast_2d(I2), axis=0), axis=0).T
        sweepSize = self.headerData['numSteps']*2
        
        self.ch1 = np.rollaxis( np.reshape( np.rollaxis( np.atleast_3d(ch1), 2, 0 ), (numGoodSweeps, sweepSize, 3) ), 0, 3 )
        self.ch2 = np.rollaxis( np.reshape( np.rollaxis( np.atleast_3d(ch2), 2, 0 ), (numGoodSweeps, sweepSize, 3) ), 0, 3 )
        
        # for k in range(np.size(self.ch1, 3)):
        #     temp1 = float(self.ch1[:,1,k]) - (fit_coef[1,1] * self.dacCounts[0:sweepSize] + fit_coef[1,0])
        #     temp2 = float(self.ch2[:,1,k]) - (fit_coef[2,1] * self.dacCounts[0:sweepSize] + fit_coef[2,0])
        #     self.ch1[:,2,k] = calib_coef[0,1]* temp1 + calib_coef[0,0] - offset_I1
        #     self.ch2[:,2,k] = calib_coef[1,1]* temp2 + calib_coef[1,0] - offset_I2
        
        '''
calib coef
1.46600914890588e-07	3.05154012782975e-10
1.86107422066320e-10	3.05182872532763e-12
	offset_I1 = 14.5e-8;%8e-8;
	offset_I2 = 0;%2.5e-8;
		temp1 = double(channel1Counts(:,1,k)) - (fit_coef(2,2) * DAC + fit_coef(2,1));
		temp2 = double(channel2Counts(:,1,k)) - (fit_coef(3,2) * DAC + fit_coef(3,1));
		channel1(:,3,k) = calib_coef(1,2)* temp1 + calib_coef(1,1) - offset_I1;
		channel2(:,3,k) = calib_coef(2,2)* temp2 + calib_coef(2,1) - offset_I2;
        '''
        
        # print(fit_coef)
        # print("size is ", np.size(fit_coef, 0), "x", np.size(fit_coef,1))
        
        

# w = WSLP()
# w.connect('COM22')
# sleep(1)
# w.takeSweep(False, [])
# sleep(10)
# print("disconnecting")
# w.disconnect()

# try:
#     name = Directory().data + '\\' + "dec_sample.mat"
#     data = sio.loadmat(name)
#     # print(data['systemData'])
# except:
#     print("error opening file")
# ch1 = data['lg']
# ch2 = data['hg']
# Vp = w.estimateVp(ch1[:,:,1])
# Te, Ne = w.estimateEEDF(ch1[:,:,1])
# print("ch1 size, (", np.size(ch1, axis = 0), ',', np.size(ch1, axis=1), ',', np.size(ch1, axis=2), ')')
# Vp = np.zeros( (np.size(ch1, axis=2),))
# for k in range( (np.size(ch1, axis=2))):
#     # di = np.diff(ch1[:,3,k])
#     # dataI = pd.DataFrame({"vals":np.diff(ch1[:,3,k]) })
#     # dI = dataI['vals'].rolling(window=11).mean()
#     # dV = (ch1[0:-1, 2, k] + ch1[1:, 2, k]) / 2
    
#     # if dV[0] > dV[-1]:
#     #     di = np.flip( di )
#     #     dI = np.flip( dI )
#     #     dV = np.flip( dV )
#     # if ( np.abs( dV[0] + dV[-1] ) > 1):
#     #     print("skipping held(?) leg")
#     #     continue # if
    
#     # ind = np.argmax( np.abs(dI[(dV<20)]) )
#     # Vp[k] = dV[ind]
#     Vp[k] = w.estimateVp(ch1, k)
#     print("Vp for ", k, " is ", Vp[k], 'V')




# w.generateSweepLeg( 10 )
# print(len(w.sweepLeg))
# print('max, min is ', w.maxCount, ', ', w.minCount)
# print(w.sweepLeg)
# 
# w = WSLP()
# w.connect("COM22")
# sleep(1)
# w.programSweep(4, 15, 0, 1)
# sleep(1)
# w.disconnect()