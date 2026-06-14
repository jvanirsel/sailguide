'''  
Created on Oct 22, 2025
Seth Gerow*
Senior Design Project

*github copilot exclusively used for 'code completions', no design, structure, or logic was writted by github copilot.
'''
import numpy as np
from Basic import PeripheralDevice
from time import sleep
from threading import Thread
from VCPThreads import MonitorThread
import scipy.io as sio
import os
from RPAconstants import *
import serial
import time
import struct
import datetime
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.signal import filtfilt, iirnotch, find_peaks
from scipy.optimize import least_squares
import matplotlib.pyplot as plt

class RPA( PeripheralDevice ):
    #RPA class subset of Peripheral Device
    #attributes inherited from SerialDevice:
    # self.setName(name)
    # self.comPort = '' : str 'COM#' # <=5
    # self.baudRate = baud
    # self.timeOut = 0.5 #seconds
    # self.comStatus = -1
    # self.eol = eol :str
    # self.cv = Condition()
    #attributes inherited from PeripheralDevice:
    # self.pollRate = pollRate
    # self.monitor = MonitorThread(self)
    # self.badPacketCounter = 0

    #method inherited from SerialDevice:
    # __init__(self, name, baud, eol):
    # connect(self, newPort): #calls doConnect as a thread
    # doConnect(self): #attempts to connect to serial port using pyserial
    # validateConnection(self): #unique to each device, checks if connection is valid
    # disconnect(self):
    # write(self, message):
    # writeByte(self, bite):
    # setName(self, newName):
    # setComPort(self, newPort):
    #methods inherited from PeriferalDevice:
    # disconnect(self)
    # doConnect(self)    
    # pollSystemData(self)
    # startMonitor(self)
    # checkPacketCounter(self, result)
    # command( self, message, returnSize=0 )

    def __init__(self):
        baud = 115200
        eol = 0xED
        pollRate = 1
        super().__init__('RPA', baud, eol, pollRate) #use parent init 
        # per second the monitor thread checks for new data
        self.monitor = MonitorThread(self) #creates monitoring thread
        self.badPacketCounter = 0 #Iterated when bad packet is received. 
        # Default operation causes disconnect when >5
        self.flgActive = -1 #flag for active mode #Need to determine what this does

        #Add any RPA specific variables here
        self.current = 0 #current reading from RPA, RPA will used continuous 
        # transmission so each packet will contain a single current and voltage reading, 
        # thus an array is not needed.
        self.voltage = 0 #voltage reading from RPA
        self.temp = 0
        self.velocity = 0
        self.density = 0
        self.pointID = -1
        self.adc_counts = 0
        self.dac_counts = 0
        self.t = 0 #time of reading from RPA. #Not sure if this should be time reading was 
        self.sweep_num = 0
        # taken on RPA or time reading was received by PC. I do not think the RPA sends time data. 
        # so it is likely the time the reading was received by PC, but should it be time requested or 
        # time received?
        self.calpoints_adc = {}
        self.calpoints_dac = {}
        
        self.cmd = None

        self.time_array = defaultdict(list)
        self.current_array = defaultdict(list)
        self.voltage_array = defaultdict(list)
        self.current_counts_array = defaultdict(list)
        self.voltage_counts_array = defaultdict(list)
        self.velocity_array = defaultdict(list)
        self.temp_array = defaultdict(list)
        self.density_array = defaultdict(list)
        self.pointID_array = defaultdict(list)
        self.sweep_num_array = defaultdict(list)

        self.comPort  = '' #COM port will be set when connected
        self.needSave = 0
        
        #location of save data. probably should not stay as my sandbox but its easiest for now
        self.filepath = Path(r'C:\SAIL\OneDrive\Plasma Chamber\IndividualSandbox\Seth Gerow\RPAData')

    ### Methods ###
    #Override of PeripheralDevice
    def getSavePath(self):
            # mm-dd-yy string
        day_folder = datetime.datetime.now().strftime('%m-%d-%y')
        # Make folder if it doesn't exist
        filepath = self.filepath/day_folder
        os.makedirs(filepath, exist_ok=True)
        return filepath
        
    def writeByte(self, byte):
        try:
            self.port.write(byte)
        except ValueError as e:
            print(e)
            
    
    def validateConnection(self):
        self.cv.acquire(1)
        print('validateConnection() method called from '+ self.name)
        self.writeByte(self.idn_command())
        pkt = self.scan_serial(timeout = 10)
        if self.parse_acknowledgement(pkt, ACK_READY):
            print('acknowledgement received')
            self.cv.release()
            return True
        else:
            print('acknowledgement not received, but something was')
            self.cv.release()
            return False
    
    def pollSystemData(self):
        return super().pollSystemData()
    
    def startMonitor(self):
        # this does nothing for now becuse I have no idea what it is supposed to do
        pass

    #RPA Specific Methods
    def readADC(self, cmd):
        if(self.comStatus == 1):
            self.thProgramSweep = Thread( target = self.doReadADC, name = self.name + '-Read-ADC', daemon = True, args=(cmd))
            self.thProgramSweep.start()
            return True
        else:
            print( self.name, " is not connected; readADC command not executed" )
            return False


    def doReadADC(self, cmd):
        self.cv.acquire(1)
        self.writeByte(cmd)
        pkt = self.scan_serial(timeout = 10)
        if self.parse_acknowledgement(pkt, ACK_COMMAND_RECEIVED):
            #print('acknowledgement received')
            try:
                return_pkt = self.scan_serial()
            except ValueError as e:
                self.cv.release()
                print(e)   
                return
            #print(f'received: {return_pkt}')
            if return_pkt[0] == DATA_ADC_HEADER or return_pkt[0] == DATA_SWP_HEADER:
                try:
                    adc_counts = self.parse_adc(return_pkt)
                except ValueError as e:
                    self.cv.release()
                    print(e)
                    return
                self.adc_counts = adc_counts
                adc_curr = self.cnts2curr(adc_counts)
                self.current = adc_curr
                #print(f'{adc_curr} nA')
                self.cv.release()
        else:
            self.cv.release()
            print('acknowledgement not received, but something was')
            return
        
    def setDAC(self, cmd):
        if(self.comStatus == 1):
            self.thProgramSweep = Thread( target = self.doSetDAC, name = self.name + '-Set-DAC', daemon = True, args=(cmd))
            self.thProgramSweep.start()
            return True
        else:
            print( self.name, " is not connected; setDAC command not executed" )
            return False
            
    def doSetDAC(self, cmd):
        self.cv.acquire(1)
        self.writeByte(cmd)
        pkt = self.scan_serial()
        if self.parse_acknowledgement(pkt, ACK_COMMAND_RECEIVED):
            try:
                return_pkt = self.scan_serial()
            except ValueError as e:
                print(e)
                self.cv.release()
                return
            if self.parse_acknowledgement(return_pkt, ACK_DAC_SET):
                self.voltage = self.cnts2volt(int.from_bytes(cmd[1:3], byteorder='little'))
                self.dac_counts = int.from_bytes(cmd[1:3], byteorder='little')
                self.cv.release()
            else:
                self.cv.release()
                print('acknowledgement not received, but something was')
                return
        else:
            self.cv.release()
            print('acknowledgement not received, but something was')
            return
        
    def send_and_save_sweep(self, cmd, filename):
        if(self.comStatus == 1):
            self.thProgramSweep = Thread( target = self.do_send_and_save_sweep, name = self.name + '-Send-Sweep', daemon = True, args=(cmd, filename))
            self.thProgramSweep.start()
            return True
        else:
            print( self.name, " is not connected; send_and_save_sweep command not executed" )
            return False

    def do_send_and_save_sweep(self, cmd, filename):
        self.cv.acquire(1)
        self.writeByte(cmd)
        sweep_data = [None] * 6  # creates [None, None, None, None, None, None] #switch to dictionary asap
        try:
            return_pkt = self.scan_serial()
        except ValueError as e:
            print(e)
        if self.parse_acknowledgement(return_pkt, ACK_COMMAND_RECEIVED):
            self.flgActive = 1
            try:
                return_pkt = self.scan_serial()
            except ValueError as e:
                self.badPacketCounter += 1
                print(e)   
            while self.flgActive == 1:
                if return_pkt[0] == DATA_ADC_HEADER or return_pkt[0] == DATA_SWP_HEADER:
                    try:
                        point_id, dac_counts, adc_counts = self.parse_sweep(return_pkt)
                    except ValueError as e:
                        self.badPacketCounter += 1
                        print(e)
                        continue
                    sweep_data[0] = self.sweep_num
                    sweep_data[1] = point_id
                    sweep_data[2] = self.cnts2curr(adc_counts)
                    sweep_data[3] = self.cnts2volt(dac_counts)
                    sweep_data[4] = adc_counts
                    sweep_data[5] = dac_counts
                    self.saveSweep(filename, sweep_data)
                    #print(f'sweep/point: {self.sweep_num},{point_id}: {sweep_data[3]} V, {sweep_data[2]} nA')
                    try:
                        return_pkt = self.scan_serial()
                    except ValueError as e:
                        self.badPacketCounter += 1
                        print(e)
                        continue
                    if return_pkt[0] == ACK_HEADER:
                        if self.parse_acknowledgement(return_pkt, ACK_SWEEP_COMPLETE):
                            print('sweep end received')
                            print(f'{self.sweep_num} sweeps complete')
                            self.flgActive = -1
                            self.cv.release()
                            self.theoretical_estimate(self.current_array, self.voltage_array)
                            return
        else:
            print('command not acknoledged when expected')
            self.cv.release()
        
    def _read_and_saveADC(self, cmd, curr, filename):
        self.readADC(cmd)
        self.saveADCcal(filename, curr)

    #File IO Methods
    def saveDACcal(self, filename, volt):
        self.t = time.time()
        self.calpoints_dac['time'] = self.t
        self.calpoints_dac['volts'] = volt
        self.calpoints_dac['counts'] = self.dac_counts
        
        # mm-dd-yy string
        day_folder = datetime.datetime.now().strftime('%m-%d-%y')
        # Make folder if it doesn't exist
        filepath = self.filepath/day_folder
        os.makedirs(filepath, exist_ok=True)
        if not filename:
            filename = 'DACCAL.mat'
        filename = filepath/filename
        print(filename)
        if os.path.exists(filename):
            # import data if its already there, then append
            data = sio.loadmat(filename)
            #remove scipy tags
            data = {k: v for k, v in data.items() if not k.startswith('_')}
            for key in self.calpoints_dac:
                data[key] = np.append(data[key], self.calpoints_dac[key])
        else:
            data = self.calpoints_dac
        print(f'saving {volt}, {self.dac_counts}')
        sio.savemat(filename, data)
        
    def saveADCcal(self, filename, curr):
        self.t = time.time()
        self.calpoints_adc['time'] = self.t
        self.calpoints_adc['current'] = curr
        self.calpoints_adc['counts'] = self.adc_counts
        
        # mm-dd-yy string
        day_folder = datetime.datetime.now().strftime('%m-%d-%y')
        # Make folder if it doesn't exist
        filepath = self.filepath/day_folder
        os.makedirs(filepath, exist_ok=True)
        print(filepath)
        if not filename:
            filename = 'ADCCAL.mat'
        filename = filepath/filename
        print(filename)
        if os.path.exists(filename):
            # import data if its already there, then append
            data = sio.loadmat(filename)
            #remove scipy tags
            data = {k: v for k, v in data.items() if not k.startswith('_')}
            for key in self.calpoints_adc:
                data[key] = np.append(data[key], self.calpoints_adc[key])
        else:
            data = self.calpoints_adc
        sio.savemat(filename, data)
            
    def saveSweep(self, filename, sweep_data):
        self.t = time.time()
        self.sweep_num = sweep_data[0]
        self.pointID = sweep_data[1]
        self.current = sweep_data[2]
        self.voltage = sweep_data[3]
        self.current_counts = sweep_data[4]
        self.voltage_counts = sweep_data[5]

        self.time_array[self.sweep_num].append(self.t)
        self.current_array[self.sweep_num].append(self.current)
        self.voltage_array[self.sweep_num].append(self.voltage)  
        self.current_counts_array[self.sweep_num].append(self.current_counts)
        self.voltage_counts_array[self.sweep_num].append(self.voltage_counts)
        self.pointID_array[self.sweep_num].append(self.pointID)
        self.sweep_num_array[self.sweep_num].append(self.sweep_num)
        
        #self.theoretical_estimate( self.current_array, self.voltage_array)
        
        self.needSave = 1

    ## Data Handling Methods ##
    def calc_checksum(self, data):
        '''Calculate XOR checksum over bytesarray'''
        cs = 0
        for byte in data:
            cs ^= byte
        return cs
    
    def decode20bit(self, byte1, byte2, byte3):
        val = (byte1 << 12) | (byte2 << 4) | (byte3 >> 4)
        if val & (1 << 19):
            val -= (1 << 20)
        return val
    
    def cnts2curr(self, adc_counts):
        a = 0.000520
        b = 250.647438
        counts = -1*adc_counts
        current = a*counts + b
        return current
    
    def cnts2volt(self, dac_counts):
        a = 0.000227
        b = -4.258004
        voltage = a * dac_counts + b #discriminator voltage
        return voltage
    
    def volt2cnts(self, voltage):
        a = 0.000227
        b = -4.258004
        dac_counts= (voltage - b)/a #discriminator voltage
        return dac_counts

    def curr2cnts(self, current):
        a = 0.000520
        b = 250.647438
        counts = -1*(current-b)/a
        return counts

    
    ## Binary Command Methods ##
    def idn_command(self):
        '''
        returns bytearray to be sent to rpa to test if it is online
        '''
        return bytes([CMD_IDN_HEADER, PACKET_FOOTER])
    
    def poll_adc_command(self,num_avgs):
        packet = struct.pack('<BBB',
                            CMD_ADC_HEADER,
                            num_avgs,
                            PACKET_FOOTER)
        return packet
    
    def set_dac_command(self,dac_volt):
        packet = struct.pack('<BHB',
                            CMD_DAC_HEADER,
                            dac_volt,
                            PACKET_FOOTER)
        return packet 
    
    def sweep_command(self, dac_volt_lower, dac_volt_upper, num_steps, step_delay_us, num_avgs):
        packet = struct.pack('<BHHHHB',
                            CMD_SWP_HEADER,
                            dac_volt_lower,
                            dac_volt_upper,
                            num_steps,
                            step_delay_us,
                            num_avgs)
        cs = self.calc_checksum(packet[1:])
        packet += bytes([cs, PACKET_FOOTER])
        return packet
    
    def parse_sweep(self, pkt):
        #print(f'received:', [hex(b) for b in pkt])
        if len(pkt) != SWP_PKT_LEN:
            self.badPacketCounter +=1
            raise ValueError('Invalid packet length')
        cs = self.calc_checksum(pkt[1:8])
        if cs != pkt[8]:
            self.badPacketCounter +=1
            raise ValueError("Checksum error: packet lost")
        pkt_id = struct.unpack('<H', pkt[1:3])[0]
        dac_count = struct.unpack('<H', pkt[3:5])[0]
        adc_counts = self.decode20bit(pkt[5], pkt[6], pkt[7])
        # print(f"datapoint {pkt_id}: dac {dac_count}, adc {adc_counts}")
        return pkt_id, dac_count, adc_counts

    def parse_adc(self, pkt):
        print(f'received:', [hex(b) for b in pkt])
        if len(pkt) != ADC_PKT_LEN:
            self.badPacketCounter +=1
            raise ValueError('Invalid packet length')
        cs = self.calc_checksum(pkt[1:4])
        if cs != pkt[4]:
            self.badPacketCounter += 1
            raise ValueError("Checksum error: packet lost")
        adc_counts = self.decode20bit(pkt[1], pkt[2], pkt[3])
        print(f'adc counts {adc_counts}')
        return adc_counts

    def parse_error(self,pkt):
        if len(pkt) != SHORT_PKT_LEN:
            self.badPacketCounter +=1
            raise ValueError('Invalid packet length')
        error_code = pkt[1]
        if error_code == ERROR_CHECKSUM_FAIL:
            raise ValueError("Error Checksum Fail")
        elif error_code == ERROR_INVALID_FRAME:
            raise ValueError("Missing Header or Footer")
        elif error_code == ERROR_INVALID_PARAMS:
            raise ValueError('Invalid Input Values')
        elif error_code == ERROR_ADC_TIMEOUT:
            raise ValueError("ADC did not respond")
        elif error_code == ERROR_DAC_FAILURE:
            raise ValueError("DAC did not respond")
        elif error_code == ERROR_OTHER:
            raise ValueError('Error')
        else:
            raise ValueError('Error')

    def parse_acknowledgement(self, pkt, expectation):
        if len(pkt) != SHORT_PKT_LEN:
            self.badPacketCounter +=1
            raise ValueError('Invalid packet length')
        if pkt[1] == expectation:
            return True
        else:
            return False

    # Serial reading
    def read_packet(self, ser, buf):
        if buf[0] == DATA_ADC_HEADER:
            expectation_length = ADC_PKT_LEN
        elif buf[0] == DATA_SWP_HEADER:
            expectation_length = SWP_PKT_LEN
        elif buf[0] == ACK_HEADER or buf[0] == ERROR_HEADER:
            expectation_length = SHORT_PKT_LEN
        else:
            raise ValueError(f'i did not get an adc, sweep, ack, or error header. Received byte: {buf[0]}')
        while len(buf) < expectation_length:
            byte = ser.read(1)
            buf.extend(byte)
        if ord(byte) != PACKET_FOOTER:
            raise ValueError(f'this is the ord error idk what it means, basically the end header was unexpected\npacket i got: {buf}')
        else:
            return buf
        
    def scan_serial(self, timeout = 10):
        """
        Scan the stream byte-by-byte to find a valid DE...AD framed packet.
        This is robust to misalignment and extra bytes.
        dont use right now, not really working
        """
        ser = self.port
        buf = bytearray()
        start = time.time()
        while time.time()-start < timeout:
            if ser.in_waiting > 0:
                byte = ser.read(1)
                buf.extend(byte)
                #print(f'buffer into read_packet():{buf}')
                pkt = self.read_packet(ser, buf)
                return pkt
                
    def theoretical_estimate(self, I, V):
        """
        ApproximateGUIfit.py
        Curve fitting RPA IV curve for a multi energy population
        """
        # =============================================================================
        # Constants
        # =============================================================================
        q  = 1.602e-19        # C (fundamental charge)
        kB = 1.380e-23        # m^2 kg s^-2 K^-1 (Boltzmann Constant)
        M  = 6.64e-26         # kg (ion mass)
        A  = 0.6              # (Effective Area)

        # =============================================================================
        # ADVANCED SMOOTHING
        # =============================================================================
        fs = 200              # sampling frequency (Hz)
        Q  = 1.0              # quality factor

        # =============================================================================
        # Check Frequencies
        # (Assumes I_meas_A and V_V are already loaded as 2-D NumPy arrays)
        # =============================================================================
        num_sweeps = len(I) 
        if num_sweeps == 0:
            return
        if num_sweeps:
            min_len = min(len(v) for v in V.values())

            V_avg = np.mean([v[:min_len] for v in V.values()], axis=0)
            I_avg = np.mean([c[:min_len] for c in I.values()], axis=0)
            
        N        = len(I_avg)
        I_fourier = np.fft.fft(I_avg)
        f        = np.arange(N) * (fs / N)
        mag      = np.abs(I_fourier) / N

        half     = slice(0, N // 2)            # first half of spectrum
        f_half   = f[half]
        mag_half = mag[half]

        min_height = mag_half.max() / 10
        locs_idx, props = find_peaks(mag_half, height=min_height)
        locs = f_half[locs_idx]
        pks  = mag_half[locs_idx]

        # =============================================================================
        # Smoothing  — design one notch per detected frequency, cascade them
        # =============================================================================
        f0_list = locs                              # notch frequencies in Hz

        # Start with the raw signal; apply each notch filter in sequence
        I_clean = I_avg.copy().astype(float)

        for f0 in f0_list:
            wo = f0 / (fs / 2)                      # normalised frequency [0, 1]
            bw = wo / Q                             # -3 dB bandwidth (normalised)
            b, a = iirnotch(wo, Q)                  # scipy equivalent of designNotchPeakIIR
            for col in range(I_clean.shape[1]):
                I_clean[:, col] = filtfilt(b, a, I_clean[:, col])

        # =============================================================================
        # Change to v_min
        # =============================================================================
        #V     = np.mean(V_avg)               # mean discriminator voltage
        v_min = []
        for val in V:
            v_min.append(np.sqrt(np.maximum(2 * q * val / M, 0)))
        

        idx   = np.argmax(v_min != 0)              # first non-zero index
        v_min   = v_min[idx:]
        I_clean = I_clean[idx:]

        #I = np.mean(I_clean)

        # =============================================================================
        # Numerical derivative  (dI/dv_min)
        # =============================================================================
        n_pts = I.shape[0] - 1
        I1 = np.zeros(n_pts)
        h  = np.zeros(n_pts)

        for i in range(n_pts):
            h[i]  = v_min[i + 1] - v_min[i]
            I1[i] = (I[i + 1] - I[i]) / h[i]

        v_min = v_min[:n_pts]

        # =============================================================================
        # Initial Guess
        # =============================================================================
        neg_I1 = -I1

        # Mean velocity — location of the peak
        peak_idx = int(np.argmax(neg_I1))
        u_0 = v_min[peak_idx]

        # Width of Gaussian — from FWHM
        half_max  = neg_I1.max() / 2
        left_arr  = np.where(neg_I1[:peak_idx] < half_max)[0]
        right_arr = np.where(neg_I1[peak_idx:] < half_max)[0]

        left_idx  = left_arr[-1]  if left_arr.size  > 0 else 0
        right_idx = right_arr[0] + peak_idx if right_arr.size > 0 else n_pts - 1

        HWHM        = (v_min[right_idx] - v_min[left_idx]) / 2
        sigma_guess = HWHM / np.sqrt(2 * np.log(2))
        B_guess     = 1 / (2 * sigma_guess**2)

        I_peak  = neg_I1.max()
        A_guess = -I_peak / u_0          # same simplification as MATLAB

        # =============================================================================
        # Curve Fit
        # =============================================================================
        def model(params, vmin):
            """I_1 = A * vmin * exp(-B * (vmin - u)^2)"""
            A_p, B_p, u_p = params
            return A_p * vmin * np.exp(-B_p * (vmin - u_p)**2)

        def residuals(params, vmin, target):
            return model(params, vmin) - target

        params0 = np.array([A_guess, B_guess, u_0])

        result = least_squares(
            residuals,
            params0,
            args=(v_min, neg_I1),
            method='trf',           # Trust Region Reflective — equivalent to lsqcurvefit
            ftol=1e-12,
            xtol=1e-12,
            gtol=1e-12,
        )
        params_fit = result.x

        # =============================================================================
        # Calculate Parameters
        # =============================================================================
        u   = params_fit[2]                                           # mean velocity (m/s)
        T_K = M / (2 * kB * params_fit[1])                           # temperature (K)
        T   = kB * T_K / q                                            # temperature (eV)
        n   = (params_fit[0] / (q * A)) * np.sqrt(np.pi / params_fit[1]) * 1e-6  # density (m^-3)

        self.velocity = u
        self.density = n
        self.temp = T
#         print(f'Mean Velocity (u): {u:.2f} m/s')
#         print(f'Temperature (T):   {T:.2f} eV')
#         print(f'Density (n):       {n:.2e} m^-3')


