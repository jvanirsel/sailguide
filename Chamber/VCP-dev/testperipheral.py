from time import sleep
from threading import Thread, Condition, Event
# from testthreads import BigThread, SingleThread
from testthreads import MonitorThread

class PeripheralClass():

    def __init__(self):
        # normal constructor?
        self.flag = False
        self.cv = Condition()
        self.event = Event()
        self.isBusy = False
        # self.cv2 = Condition()
        self.monitor = MonitorThread(self, self.event)
        # self.bigThread = BigThread(self)


    def startMonitor(self):  #starts thread
        print("startMonitor() method called from Object")
        # print("monitor daemon status is " + str(self.monitor.daemon))
        self.monitor.start()
    
    
    def task(self):
        self.taskThread = Thread( target = self.tryTask, name = 'Tasker')#, args = (self,) )
        self.taskThread.start()
    
    def tryTask(self):
        print("tryTask() method is called from Object. Waiting...")
        
        if(self.event.wait(6)): # manual lock method
            print("Object starts task")
            self.isBusy = True
            sleep(0.1)
            print("Object completes task")
            self.isBusy = False
            print('object tryTask thread is finished')
        else:
            print("tryTask timed out")       
            
    def lockTask(self):
        self.lockThread = Thread( target = self.tryLockTask, name = 'Locker')
        self.lockThread.start()
        
    def tryLockTask(self):
        print("  tryLockTask method called from object")
        
        print("  Locker acquires lock")
        self.cv.acquire(7)
        print("  Locker does a thing...")
        print("   0/2" )
        sleep(0.6)
        print("   1/2" )
        sleep(0.6)
        print("   2/2" )
        print("  Locker releases lock")
        self.cv.release()
        
        
        print('  locker thread finished')
   
    
###################################################################
    def startConnect(self):
        print(" Peripheral starts connection")
        # self.thread = BigThread(self)
        # # OR
        # self.thread = SingleThread(self)
        # # OR
        self.thread = Thread( target= self.connect)
        self.thread.start()
        print(" peripheral finished startConnect method")

    def connect(self):
        print("     Peripheral starts connecting from thread")
        sleep(1)
        self.flag = True
        print("     Peripheral has data from thread")
        
####################################################################
print("\n\nStarting...\n")
thing = PeripheralClass()
thing.startMonitor()
print("Test 1: lockTask called during monitor action")
sleep(2)
thing.lockTask()
sleep(12)

print("Test 2: Monitor action called during lockTask")
thing.lockTask()
sleep(5)
# thing.task()
# sleep(7)
print("trying to kill thread")
thing.monitor.counter = 15 # sheesh
thing.monitor.join()
print("'tis finished\n")