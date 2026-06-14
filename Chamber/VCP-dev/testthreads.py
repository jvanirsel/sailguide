from time import sleep
from threading import Thread

class MonitorThread(Thread):
    #Constructor
    def __init__(self, Owner, event):
        super().__init__()
        # Default vals
        self.owner = Owner
        self.event = event
        self.name = "Monitorer"
        self.daemon = True
        
    # Functions
    def run(self):
        print("     Monitor starts thread")
        self.counter = 0
        

        while( self.counter < 5 ):
            # # Event method:
            # if not self.owner.isBusy:   # necessary to ensure monitor doesn't overwrite a callback
            #     print("    Monitor does things... ") #"(count " + str(self.counter) + ')')
            #     self.event.clear()
            #     for n in range(5):
            #         sleep(1)
            #         print("    " + str(n+1))
            #     print("    Monitor finishes task, sets event")
            #     self.event.set()
            # print("    Monitor starts 2 second wait to repeat")
            # sleep(2)
            
            # Lock method:
            print("     Monitor acquires lock")
            self.owner.cv.acquire(2)
            
            print("     Monitor does things... ") #"(count " + str(self.counter) + ')')
            for n in range(5):
                sleep(1)
                print("       " + str(n+1) + "/5")
            print("     Monitor finishes task, releases lock")
            self.owner.cv.release()
            
            print("     Monitor starts 2 second wait to repeat")
            sleep(2)
        
        print("     Monitor is ended.")
    
    
    
###############################################################################        


class BigThread(Thread):
    # Constructor
    def __init__(self, Owner):
        #execute base constructor
        Thread.__init__(self)
        #set deafult value
        self.owner = Owner
        self.owner.flag = False      #since it's not inherent to this class, do I leave him here?

    # Function
    def run(self):
        print("     Running BigThread")
        #Spin off connector thread
        subThread = ConnectorThread()
        subThread.start()

        # wait for connector thread to finish
        subThread.join()

        # Get value from subthread 
        self.owner.flag = subThread.flag
        print("     BigThread finishes run")


class ConnectorThread(Thread):
    # Constructor
    def __init__(self):
        #execute base constructor
        Thread.__init__(self)
        #set deafult value
        self.flag = False

    # Function
    def run(self):
        print("         Running ConnectorThread")
        #block for a moment
        sleep(1)
        # Store new data
        self.flag = True
        print("         ConnectorThread has Data")

class SingleThread(Thread):
    # Constructor
    def __init__(self, Owner):
        #execute base constructor
        Thread.__init__(self)
        #set deafult value
        self.owner = Owner
        self.owner.flag = False      #since it's not inherent to this class, do I leave him here?
        # self.flag = False

    # Function
    def run(self):
        print("         Running ConnectorThread")
        #block for a moment
        sleep(1)
        # Store new data
        self.owner.flag = True
        print("         ConnectorThread has Data")