import tkinter as tk
import tkinter.ttk as ttk

class StatusLight( tk.Button ):
    #Constructor
    def __init__(self, root):
        # self.green = tk.PhotoImage(file = 'greenlight.png')
        super().__init__(root, relief = 'flat', borderwidth = 0)
        self.green = tk.PhotoImage(file = 'greenlight.png')
        
    def setGreen(self):
        print('setGreen method called')
        self['image'] = self.green
        print('setGreen method ended')        
        


class subFrame( ttk.Frame ):
    def __init__(self, root, name, widget, lists):
        super().__init__(root)
        self.lists = lists
        self.widget = widget
        self.widget['text'] = name
        self.widget.pack()
        
    def changeVal1(self):
        self.lists.changeVal1()
        
    def changeVal2(self):
        self.lists.changeVal2()
        
    def printList(self):
        return self.lists.printList()
        
        

class bigFrame( ttk.Frame ):
    def __init__(self, root):
        super().__init__(root)
        self.btThing = tk.Button(self)
        self.label = tk.Label(self)
        self.lists = lists()
        self.frame1 = subFrame( self, 'fr1', self.btThing, self.lists)
        self.frame2 = subFrame(self, 'fr2', self.label, self.lists)
        
        
    def packThings(self):
        self.frame1.pack()
        self.frame2.pack()
        
    def printList(self):
        return self.lists.printList()


class lists():
    def __init__(self):
        self.lists = ["0", "1", '2', '3', '4', '5', '6', '7']
        
    def changeVal1(self):
        self.lists[1] = 'Q'
        
    def changeVal2(self):
        self.lists[2] = "Z"
        
    def printList(self):
        return self.lists
    
# GUI
win= tk.Tk()
win.title("Button status light test")

#Define the size of the tkinter frame
win.geometry("700x300")


# Test 1: light
# light1 = StatusLight(win)
# light1.pack()
# win.after(1000, light1.setGreen )
# # btSetColor = tk.Button( text = 'greenify', command = light1.setGreen)

frame = bigFrame(win)
frame.pack()
frame.packThings()



print(' bigFrames list: ', frame.printList())
print( ' frame 1 lsits: ', frame.frame1.printList())
print( ' frame 2 litsts: ', frame.frame2.printList())
print('changing val1')
frame.frame1.changeVal1()
print(' bigFrames list: ', frame.printList())
print( ' frame 1 lsits: ', frame.frame1.printList())
print( ' frame 2 litsts: ', frame.frame2.printList())
print('changing val2')
frame.frame2.changeVal2()
print(' bigFrames list: ', frame.printList())
print( ' frame 1 lsits: ', frame.frame1.printList())
print( ' frame 2 litsts: ', frame.frame2.printList())



win.mainloop()
print("test done.")