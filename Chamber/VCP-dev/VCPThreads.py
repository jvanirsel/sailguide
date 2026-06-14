from threading import Thread, Condition
from time import sleep

class MonitorThread(Thread):
    #Constructor
    def __init__(self, Owner):
        super().__init__()
        self.owner = Owner
        self.name = Owner.name + "-Monitor"
        self.daemon = True

    # Functions
    def run(self):
        print("     "+ self.name + " starts thread")
        while( self.owner.comStatus == 1 ):
            try:
                self.owner.checkPacketCounter( self.owner.pollSystemData() )
            except Exception as e:
                print("!!!     " + self.name + " can't poll system data?")
                print(" error is ", e)
            # print("     " + self.name + " starts wait to repeat")
            sleep(1/self.owner.pollRate)

        print("     " + self.name + " is ended.")
        
class DataRelayThread(Thread):
    #Constructor
    def __init__(self, Owner):
        super().__init__()
        self.owner = Owner
        self.name = Owner.name + "-Rx-Monitor"
        self.daemon = True

    # Functions
    def run(self):
        print("     "+ self.name + " starts thread")
        while self.owner.comStatus == 1:
            try:
                if self.owner.port.in_waiting > 0:
                    self.owner.pollRx()
            except:
                print("! Error monitoring on " + self.name)
            sleep(.2)
        print("     " + self.name + " is ended.")
        
