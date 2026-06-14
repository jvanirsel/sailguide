from time import sleep
from datetime import date, time
from misc import Directory
import os.path
import pandas

class ExcelManager():
    def __init__(self):
        self.path = Directory().logs + '\\'

    def fileName(self):
        today = date.today()
        name = 'SAIL_Chamber_Log_' + today.strftime("%m-%d-%Y") + '.csv'
        return name


    def saveData(self, data):
        path = self.path + self.fileName()

        # Make if DNE
        if not os.path.isfile(path):
            df = pandas.DataFrame([], columns=['Time', 'Pressure', 'PCS setpoint', 'Motor Z', 'Motor T', 'Heat1 Setpoint', 'Heat1, V', 'Heat1, A', 'Heat2 Setpoint', 'Heat2, V', 'Heat2, A', 'Bias Setpoint', 'Bias, V', 'Bias, A', ])
            df.to_csv(path, index=False, header=True)

        try:
            df = pandas.DataFrame(data)
            df.to_csv( path, index=False, header = False, mode = 'a' )
        except:
            print("Error saving data to CSV")

   


# x = ExcelManager()
# data = {'Time':['8:16'],
#         'Pressure':1, 'PCS setpoint':2, 'Motor Z':100, 'Motor T':0, 'Heat1 Setpoint':1, 'Heat1, V':1, 'Heat1, A':0, 'Heat2 Setpoint':1, 'Heat2, V':1, 'Heat2, A':1, 'Bias Setpoint':1, 'Bias, V':1, 'Bias, A':0 }
# x.saveData( data )