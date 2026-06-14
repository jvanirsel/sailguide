import serial as s
import numpy as np
import pandas as pd
import time

from Lesker import Lesker392
from PressureControlSystem import PressureController

end_loop_flag = False
counter = 0

###     ~~~~    ~~~~    ###
# Parameters
str_port2 = "COM9"
period = 0.25 #- 0.226            #give first term for intended period
runTime = 11 * 60            # minutes
print_every = 8
filename = "read_pressures_120s_upper.csv"
plotMe = False # True

usePCSFlag = True
maxCounter = 120 / period        # in seconds
###     ~~~~    ~~~~    ###

# Create objects
L392 = Lesker392()
PCS = PressureController(L392)
data = np.empty((0,3))

L392.connect('COM9')
# time.sleep(2)
PCS.connect("COM15")

# pressureSets = [ b'#02s2.00E-04\r', b'#02s3.00E-04\r', b'#02s8.00E-04\r', b'#02s5.50E-04\r' ]
# numberSets = [ 200, 300, 800, 550 ]
time.sleep(5)



# PCS.setTargetSetpoint('2e-4')

# PCS.txSetpoint('2e-4')

# PCS.enableControl()
print("entering loop...")
while L392.comStatus:
    time.sleep(0.5)
print("exiting loop...")


# Test serial connection


'''
print("done counting")

# Convert to csv file
df = pd.DataFrame(data)
df.columns = ["Time from start (s)", "Pressure Setpoint (uTorr)", "Lesker Pressure (Torr)" ]
df.to_csv(filename, index = False)
'''


# Disconnect from Pfeiffer
print('disconnected')
# PCS.disableControl()

time.sleep(0.5)
L392.disconnect()
PCS.disconnect()

