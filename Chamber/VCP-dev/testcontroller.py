from time import sleep
from threading import Thread
from testperipheral import PeripheralClass

class ControllerClass():

    def __init__(self):
        # normal constructor here, then
        self.peripheral1 = PeripheralClass()
        self.startConnect()

        sleep(4)
        self.checkStatus()
        
    def startConnect(self):
        print("Callback initiates connect event")
        self.peripheral1.startConnect()
        print("Big controller triggers 'Connecting' virtual event")


    def checkStatus(self):
        print("~~ Big Controller finds peripheral status to be: ~~")
        print(self.peripheral1.flag)
        print("~~   ~~")

cont = ControllerClass()