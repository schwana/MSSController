import random
import os
import socket
import time
import matplotlib
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np
from tkinter import filedialog

##from tkinter import * 
##
##import matplotlib.pyplot as plt
##
##import numpy as np
##import tkinter as tk
##root = tk.Tk()
##import matplotlib
matplotlib.use("TkAgg")

##from matplotlib.backends.backend_tkagg import FigureCanvasTk, NavigationToolbar2Tk
##from matplotlib.figure import Figure

N=0
root = tk.Tk()
fig = plt.Figure()
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack()
ax = fig.add_subplot(111)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()


        
class GraphFrame(tk.Frame):

    def __init__(self, master=None):
        
        tk.Frame.__init__(self, master)   
        self.master = master
        self.init_window()

    def init_window(self):

        self.master.title("SpecView")
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.NONE)

        # creating a menu instance
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label="Open", command=self.openFile)
        file.add_command(label="Exit", command=self.exit)
        menu.add_cascade(label="File", menu=file)

        edit = tk.Menu(menu)
        edit.add_command(label="Undo")
        menu.add_cascade(label="Edit", menu=edit)
        


    
    def exit(self):
        exit()

    def openFile(self):
        #Connect to instrument
        print ("Connecting to mass spec")
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(('localhost',1090))
        print (s.recv(1024))

        #Login
        s.send(b'login i,pw \r\n')
        time.sleep(1)
        print (s.recv(1024))
        time.sleep(1)
        s.send(b'ver\r\n')
        time.sleep(1)
        print (s.recv(1024))

        #Set Initial Source Voltage
        s.send(b'SetSourceOutput IE,1300.0000\r\n')
        time.sleep(10)
        print (s.recv(1024))
        s.send(b'SetAcqPeriod 100\r\n')
        time.sleep(1)
        print ("SetAcqPeriod",s.recv(1024))

        #Scan across peak
        SV=1300.0
        TV=1450.0
        global spectrum
        iE_=[]
        L5_=[]
        L4_=[]
        L3_=[]
        L2_=[]
        L1_=[]
        Ax_=[]
        H1_=[]
        H2_=[]
        H3_=[]
        H4_=[]
        global iE
        global L5
        global L4
        global L3
        global L2
        global L1
        global Ax
        global H1
        global H2
        global H3
        global H4
        global N
 
        while SV < TV:
            BStr=("SetSourceOutput IE,")
            CStr=(str(SV)+"\r\n")
            AStr=BStr+CStr
            s.send(str.encode(AStr))
            time.sleep(.2)
            IEreturn=(s.recv(1024))

            s.send(b'StartAcq 1,XX\r\n')
            time.sleep(.2)
            returnString=s.recv(1024)
            time.sleep(.2)

            #Separate the string
            spec=(returnString.decode("utf-8"))
            rS=(str(SV)+","+spec)
            rS=rS[0:-5]
            spectrum=rS.split(',')
            print (spectrum)
            print (SV, "Ax", spectrum[13], "L2", spectrum[11], "L4", spectrum[9],)


            iE_.append(float(spectrum[0]))
            L5_.append(float(spectrum[8]))
            L4_.append(float(spectrum[9]))
            L3_.append(float(spectrum[10]))
            L2_.append(float(spectrum[11]))
            L1_.append(float(spectrum[12]))
            Ax_.append(float(spectrum[13]))
            H1_.append(float(spectrum[14]))
            H2_.append(float(spectrum[15]))
            H3_.append(float(spectrum[16]))
            H4_.append(float(spectrum[16]))
     
            iE=iE_
            L5=L5_
            L4=L4_
            L3=L3_
            L2=L2_
            L1=L1_
            Ax=Ax_
            H1=H1_
            H2=H2_
            H3=H3_
            H4=H4_

            N=len(iE)
            print (N,"N")
            
            p=GraphFrame.plot()


            
            SV=SV+0.2

        s.send(b'SetSourceOutput IE,1100.0000\r\n')
        time.sleep(0.2)
        print (s.recv(1024))    
        s.close()

        self.outputData(iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4)

    def outputData(self, iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4):
        print("Output Data to File")

        os.chdir("c:\\MSSData")

        file_to_open = "ScanNum.txt"
        print (file_to_open)

        #Get current helium run number
        fo = open(file_to_open, "r")
        ScanNum = fo.readline()
        fo.close()

        print ("Scan Number",ScanNum)


        FileName = 'Scan'+ScanNum+'.dat'

        #Read Inlet Line


        foRun = open(FileName,"a")
        #Collected data
        for x in range (0, len(iE)):

            outputString=(str(iE[x])+","+str(L5[x])+","+
                          str(L4[x])+","+str(L3[x])+","+
                          str(L2[x])+","+str(L1[x])+","+
                          str(Ax[x])+","+str(H1[x])+","+
                          str(H2[x])+","+str(H3[x])+","+str(H4[x]))
            
            foRun.write(outputString+'\n')

        foRun.close()
        
        foUpdate = open("ScanNum.txt", "w")

        print (type(ScanNum))
        
        S=int(float(ScanNum))
        S=S+1
        
        foUpdate = open("ScanNum.txt", "w")
        
        
        foUpdate.write(str(S))

        foUpdate.close()       

    
    def plot():

        ax.clear()
        #Check to see what checkboxes are ticked.
        if Controls.L5_checked.get():
            ax.plot(iE,L5,color='green')
        
        if Controls.L4_checked.get():
            ax.plot(iE,L4,color='red')

        if Controls.L3_checked.get():
            ax.plot(iE,L3,color='blue')

        if Controls.L2_checked.get():
            ax.plot(iE,L2,color='cyan')

        if Controls.L1_checked.get():
            ax.plot(iE,L1,color='yellow')

        if Controls.Ax_checked.get():
            ax.plot(iE,Ax,color='magenta')            

        if Controls.H1_checked.get():
            ax.plot(iE,H1,color='black')

        if Controls.H2_checked.get():
            ax.plot(iE,H2,color='0.25')              

        if Controls.H3_checked.get():
            ax.plot(iE,H3,color='0.5')  

        if Controls.H4_checked.get():
            ax.plot(iE,H4,color='0.75')

            
        fig.canvas.draw_idle()
        root.update()
        return 1

    def UpdatePlot():
        #Check to see if a scan is loaded. If iE is empty then dont call the plot
        print ("N", N)
        if (N>0):
            p=GraphFrame.plot()
##        else:
##            print ("iE off")

  
class Controls(tk.Frame):
    
    def __init__(self, root):
        tk.Frame.__init__(self, root)


    def callback(*args):
        print ("variable changed!")
        GraphFrame.UpdatePlot()
        
    L5_checked = tk.IntVar()
    L5_checked.trace("w", callback)
    L5_checked.set(0)
    
    L4_checked = tk.IntVar()
    L4_checked.trace("w", callback)
    L4_checked.set(1)

    L3_checked = tk.IntVar()
    L3_checked.trace("w", callback)
    L3_checked.set(0)

    L2_checked = tk.IntVar()
    L2_checked.trace("w", callback)
    L2_checked.set(1)

    L1_checked = tk.IntVar()
    L1_checked.trace("w", callback)
    L1_checked.set(0)

    Ax_checked = tk.IntVar()
    Ax_checked.trace("w", callback)
    Ax_checked.set(1)
    
    H1_checked = tk.IntVar()
    H1_checked.trace("w", callback)
    H1_checked.set(0)

    H2_checked = tk.IntVar()
    H2_checked.trace("w", callback)
    H2_checked.set(0)

    H3_checked = tk.IntVar()
    H3_checked.trace("w", callback)
    H3_checked.set(0)

    H4_checked = tk.IntVar()
    H4_checked.trace("w", callback)
    H4_checked.set(0)



    c1=tk.Checkbutton(root, text="L5", onvalue=1, offvalue=0, variable=L5_checked)
    c2=tk.Checkbutton(root, text="L4", onvalue=1, offvalue=0, variable=L4_checked)
    c3=tk.Checkbutton(root, text="L3", onvalue=1, offvalue=0, variable=L3_checked)
    c4=tk.Checkbutton(root, text="L2", onvalue=1, offvalue=0, variable=L2_checked)
    c5=tk.Checkbutton(root, text="L1", onvalue=1, offvalue=0, variable=L1_checked)
    c6=tk.Checkbutton(root, text="Ax", onvalue=1, offvalue=0, variable=Ax_checked)
    c7=tk.Checkbutton(root, text="H1", onvalue=1, offvalue=0, variable=H1_checked)
    c8=tk.Checkbutton(root, text="H2", onvalue=1, offvalue=0, variable=H2_checked)
    c9=tk.Checkbutton(root, text="H3", onvalue=1, offvalue=0, variable=H3_checked)
    c10=tk.Checkbutton(root, text="H4", onvalue=1, offvalue=0, variable=H4_checked)

    
    c1.pack(side="left", fill="x")
    c2.pack(side="left", fill="x")
    c3.pack(side="left", fill="x")
    c4.pack(side="left", fill="x")
    c5.pack(side="left", fill="x")
    c6.pack(side="left", fill="x")
    c7.pack(side="left", fill="x")
    c8.pack(side="left", fill="x")
    c9.pack(side="left", fill="x")
    c10.pack(side="left", fill="x")
        
    





       
        
        
# root window created. Here, that would be the only window, but
# you can later have windows within windows.



root.geometry("800x600")

#creation of an instance
graph = GraphFrame(root)
controls=Controls(root)

graph.pack(side="left", fill="x")
controls.pack(side="bottom", fill="x")


if controls.L5_checked.get():
    print ("checked")


print (controls.L5_checked.get())     

#mainloop 
root.mainloop()
