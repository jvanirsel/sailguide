import tkinter as tk
import tkinter.ttk as ttk
from VCP_View import View
from controller import PeripheralController
from PressureControlSystem import PressureController
from Lesker import Lesker392
from MotorController import MotorController
from BKPrecision import BKP9115
from SLP import WSLP
from PNI import PNI
from misc import setIcon
from RPA import RPA

###############################################################################
#######################  CHECK CONTROLLER'S SLACK OPTION ######################
###############################################################################
class VirtualControlPanelApp( tk.Tk ):
    def __init__(self):
        super().__init__()
        
        # create model components
        self.model = {}
        self.model['mc'] = MotorController()
        self.model['l392'] = Lesker392()
        self.model['pcs'] = PressureController( self.model['l392'] )
        self.model['heat1'] = BKP9115('Heat #1')
        self.model['heat2'] = BKP9115('Heat #2')
        self.model['bias'] = BKP9115('Bias')
        self.model['wslp'] = WSLP()
        self.model['pni'] = PNI()
        self.model['rpa'] = RPA()
        
        # create View component frame
        print("creating view...")
        self.geometry( "1800x1000" )
        self.state('zoomed')
        # setIcon(self) # Really slow for some reason. Would like to replace with something else?
        self.title('SAIL Virtual Control Panel')

        self.view = View(self)
        self.columnconfigure( index=0, weight=0 )
        self.columnconfigure( index=1, weight=0 )
        self.columnconfigure( index=2, weight=1 )
        self.columnconfigure( index=3, weight=0 )
        self.columnconfigure( index=4, weight=1 )
        self.rowconfigure( index=0, weight=1 )
        self.rowconfigure( index=1, weight=1 )
        self.view.grid( row = 0, column = 0, sticky='nsew' )
        
        
        # create controller
        print("creating controller...")
        self.controller = PeripheralController( self, self.model, self.view )
        self.controller.bindControlNodes()
        
        # Start things going
        self.controller.startUpdateViewStatusLoop() # Starts up controller loop
        self.after(500, self.view.updateDisplay )  # Starts up view data update loop
        
        
    def closeWindow(self):
        # force csv save
        self.controller.log.numData = self.controller.log.saveNum+1
        self.controller.updateViewData()
        print('deleting...')
        self.controller._kill_all()
        self.destroy()
        del self.view.root # needed to kill controller thread??
        
        
        
if __name__ == '__main__':    
    app = VirtualControlPanelApp()
    app.protocol('WM_DELETE_WINDOW', app.closeWindow )
    
    # app.after() # start update check
    app.mainloop()
else:
    print('help?')
