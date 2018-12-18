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


matplotlib.use("TkAgg")


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
        file.add_command(label="Run", command=self.openFile)
        file.add_command(label="Exit", command=self.exit)
        menu.add_cascade(label="Scan", menu=file)

        edit = tk.Menu(menu)
        edit.add_command(label="Undo")
        menu.add_cascade(label="Edit", menu=edit)
            
    def exit(self):
        exit()

    def openFile(self):
        if Controls.FS_checked.get():
            print("Fast Scan")
            FastScan=True
        else:
            print("Slow Scan")
            FastScan=False            
        
        #Connect to instrument
        print ("Connecting to mass spec")
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(('localhost',1090))
        print (s.recv(1024).decode("utf-8"))

        #Login
        s.send(b'login i,pw \r\n')
        time.sleep(0.2)
        print (s.recv(1024).decode("utf-8"))
        time.sleep(0.2)
        s.send(b'ver\r\n')
        time.sleep(0.2)
        print ("Version"+s.recv(1024).decode("utf-8"))

        #Set Initial Source Voltage
        print ("Initialise Source Voltage")
        s.send(b'SetSourceOutput IE,1265.0000\r\n')
        time.sleep(1)
        Dummy=(s.recv(1024).decode("utf-8"))
        s.send(b'SetAcqPeriod 1000\r\n')
        time.sleep(0.2)
        Dummy= ("SetAcqPeriod",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))

      
        
        #Scan across peak
        global spectrum
        rS_=[]
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
        print ("Start Scan")

        scans=0
        total_scans=5

        Ax_BL=0
        L2_BL=0
        L4_BL=0
        Ax_Peak=0
        L2_Peak=0
        L4_Peak=0

        while scans < total_scans:
            SV_BL=0
            TV_BL=30
            SV_Peak=0
            TV_Peak=TV_BL
            StepSize=1

            IE_Baseline=1526
            IE_Peak=1803

            #print ("Scans Number",scans+1)
            
            print ("Scans Number",scans,"Voltage",SV_BL+SV_Peak)
            BStr=("SetSourceOutput IE,")
            CStr=(str(IE_Baseline)+"\r\n")
            AStr=BStr+CStr
            s.send(str.encode(AStr))
            time.sleep(0.1)
            IEreturn=(s.recv(1024))
            time.sleep(0.1)    
            time.sleep(300)            

            while SV_BL < TV_BL:
                #print ("Scans Number",scans,"Voltage",SV_BL)
                BStr=("SetSourceOutput IE,")
                CStr=(str(IE_Baseline)+"\r\n")
                AStr=BStr+CStr
                s.send(str.encode(AStr))
                time.sleep(0.1)
                IEreturn=(s.recv(1024))
                time.sleep(0.1)
                s.send(b'StartAcq 1,XX\r\n')
                time.sleep(1.1)
                returnString=s.recv(1024)
                time.sleep(0.1)
                if FastScan:
                  rS_IE=("0,0")
                  rS_YF=("0,0")
                  rS_YB=("0,0")
                  rS_EE=("0,0")
                  rS_IR=("0,0")
                  rS_TV=("0,0")
                  rS_FC=("0,0")
                  rS_FV=("0,0")
                  rS_TC=("0,0")
                  rS_EC=("0,0")
                else:
                    #Get readbacks of voltages
                    sleepyTime=0.1
                    s.send(b'GSO IE\r\n')
                    time.sleep(sleepyTime)
                    rS_IE=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_IE = rS_IE.replace('\n', ' ').replace('\r', '')

                    s.send(b'GSO YF\r\n')
                    time.sleep(sleepyTime)
                    rS_YF=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_YF = rS_YF.replace('\n', ' ').replace('\r', '')


                    s.send(b'GSO YB\r\n')
                    time.sleep(sleepyTime)
                    rS_YB=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_YB = rS_YB.replace('\n', ' ').replace('\r', '')
                  

                    s.send(b'GSO EE\r\n')
                    time.sleep(sleepyTime)
                    rS_EE=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_EE = rS_EE.replace('\n', ' ').replace('\r', '')
                    

                    s.send(b'GSO IR\r\n')
                    time.sleep(sleepyTime)
                    rS_IR=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_IR = rS_IR.replace('\n', ' ').replace('\r', '')
           

                    s.send(b'GSO TV\r\n')
                    time.sleep(sleepyTime)
                    rS_TV=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_TV = rS_TV.replace('\n', ' ').replace('\r', '')


                    s.send(b'GSO FC\r\n')
                    time.sleep(sleepyTime)
                    rS_FC=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_FC = rS_FC.replace('\n', ' ').replace('\r', '')
          

                    s.send(b'GSO FV\r\n')
                    time.sleep(sleepyTime)
                    rS_FV=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_FV = rS_FV.replace('\n', ' ').replace('\r', '')


                    s.send(b'GSO TC\r\n')
                    time.sleep(sleepyTime)
                    rS_TC=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_TC = rS_TC.replace('\n', ' ').replace('\r', '')
                     

                    s.send(b'GSO EC\r\n')
                    time.sleep(sleepyTime)
                    rS_EC=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_EC = rS_EC.replace('\n', ' ').replace('\r', '')


                rS_String=(","+str(rS_IE) + ","+str(rS_YF)+ ","+str(rS_YB)+ "," +
                            rS_EE+ "," +
                            rS_IR+ "," +
                            rS_TV+ "," +
                            rS_FC+ "," +
                            rS_FV+ "," +
                            rS_TC+ "," +
                            rS_EC+ ",")

                #Separate the string
                spec=(returnString.decode("utf-8"))
                rS=(str(SV_BL)+","+spec)
                rS=rS[0:-5]
                spectrum=rS.split(',')

                #print (spectrum)

                rS_.append(rS_String)
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
                rS=rS_

                N=len(iE)
               # print (N,"N")
                
                p=GraphFrame.plot()

                Ax_BL=Ax_BL+float(spectrum[13])
                L2_BL=L2_BL+float(spectrum[11])
                L4_BL=L4_BL+float(spectrum[9])

                


                
                SV_BL=SV_BL+StepSize

            print ("Scans Number",scans,"Voltage",SV_BL+SV_Peak)
            BStr=("SetSourceOutput IE,")
            CStr=(str(IE_Peak)+"\r\n")
            AStr=BStr+CStr
            s.send(str.encode(AStr))
            time.sleep(0.1)
            IEreturn=(s.recv(1024))
            time.sleep(0.1)    
          #  time.sleep(60)
            
            while SV_Peak < TV_Peak:
                #print ("Scans Number",scans,"Voltage",SV_BL+SV_Peak)
                BStr=("SetSourceOutput IE,")
                CStr=(str(IE_Peak)+"\r\n")
                AStr=BStr+CStr
                s.send(str.encode(AStr))
                time.sleep(0.1)
                IEreturn=(s.recv(1024))
                time.sleep(0.1)
                s.send(b'StartAcq 1,XX\r\n')
                time.sleep(1.1)
                returnString=s.recv(1024)
                time.sleep(0.1)
                if FastScan:
                  rS_IE=("0,0")
                  rS_YF=("0,0")
                  rS_YB=("0,0")
                  rS_EE=("0,0")
                  rS_IR=("0,0")
                  rS_TV=("0,0")
                  rS_FC=("0,0")
                  rS_FV=("0,0")
                  rS_TC=("0,0")
                  rS_EC=("0,0")
                else:
                    #Get readbacks of voltages
                    sleepyTime=0.1
                    s.send(b'GSO IE\r\n')
                    time.sleep(sleepyTime)
                    rS_IE=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_IE = rS_IE.replace('\n', ' ').replace('\r', '')

                    s.send(b'GSO YF\r\n')
                    time.sleep(sleepyTime)
                    rS_YF=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_YF = rS_YF.replace('\n', ' ').replace('\r', '')


                    s.send(b'GSO YB\r\n')
                    time.sleep(sleepyTime)
                    rS_YB=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_YB = rS_YB.replace('\n', ' ').replace('\r', '')
                  

                    s.send(b'GSO EE\r\n')
                    time.sleep(sleepyTime)
                    rS_EE=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_EE = rS_EE.replace('\n', ' ').replace('\r', '')
                    

                    s.send(b'GSO IR\r\n')
                    time.sleep(sleepyTime)
                    rS_IR=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_IR = rS_IR.replace('\n', ' ').replace('\r', '')
           

                    s.send(b'GSO TV\r\n')
                    time.sleep(sleepyTime)
                    rS_TV=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_TV = rS_TV.replace('\n', ' ').replace('\r', '')


                    s.send(b'GSO FC\r\n')
                    time.sleep(sleepyTime)
                    rS_FC=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_FC = rS_FC.replace('\n', ' ').replace('\r', '')
          

                    s.send(b'GSO FV\r\n')
                    time.sleep(sleepyTime)
                    rS_FV=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_FV = rS_FV.replace('\n', ' ').replace('\r', '')


                    s.send(b'GSO TC\r\n')
                    time.sleep(sleepyTime)
                    rS_TC=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_TC = rS_TC.replace('\n', ' ').replace('\r', '')
                     

                    s.send(b'GSO EC\r\n')
                    time.sleep(sleepyTime)
                    rS_EC=s.recv(1024).decode("utf-8")
                    time.sleep(sleepyTime)
                    rS_EC = rS_EC.replace('\n', ' ').replace('\r', '')


                rS_String=(","+str(rS_IE) + ","+str(rS_YF)+ ","+str(rS_YB)+ "," +
                            rS_EE+ "," +
                            rS_IR+ "," +
                            rS_TV+ "," +
                            rS_FC+ "," +
                            rS_FV+ "," +
                            rS_TC+ "," +
                            rS_EC+ ",")

                #Separate the string
                spec=(returnString.decode("utf-8"))
                rS=(str(SV_Peak+SV_BL)+","+spec)
                rS=rS[0:-5]
                spectrum=rS.split(',')

                #print (spectrum)

                rS_.append(rS_String)
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
                rS=rS_

                N=len(iE)
               # print (N,"N")
                
                p=GraphFrame.plot()

                Ax_Peak=Ax_BL+float(spectrum[13])
                L2_Peak=L2_BL+float(spectrum[11])
                L4_Peak=L4_BL+float(spectrum[9])
                
                SV_Peak=SV_Peak+StepSize

            

            s.send(b'SetSourceOutput IE,1100.0000\r\n')
            time.sleep(0.2)
            print (s.recv(1024))    
            

            self.outputData(iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4,rS_)

            Ax_Level=(Ax_Peak-Ax_BL)/TV_BL
            L2_Level=(L2_Peak-L2_BL)/TV_BL
            L4_Level=(L4_Peak-L4_BL)/TV_BL

            print (Ax_BL)
            print (L2_BL)
            print (L4_BL)

            print (Ax_Peak)
            print (L2_Peak)
            print (L4_Peak)
            
            print ("Ax: ",Ax_Level)
            print ("L2: ",L2_Level)
            print ("L4: ",L4_Level)
            

            R44_45=(100*Ax_Level)/L2_Level
            R44_46=(100*Ax_Level)/L4_Level

            print (R44_45)
            print (R44_46)

            #Reset all the arrays

            iE.clear()
            L5.clear()
            L4.clear()
            L3.clear()
            L2.clear()
            L1.clear()
            Ax.clear()
            H1.clear()
            H2.clear()
            H3.clear()
            H4.clear()
            rS_.clear()
            
            scans=scans+1     

        s.close()
        

    def outputData(self, iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4,rS_):
        print("Output Data to File")

        os.chdir("c:\\MSSDataPH")

        file_to_open = "ScanNum.txt"
        #print (file_to_open)

        #Get current helium run number
        fo = open(file_to_open, "r")
        ScanNum = fo.readline()
        fo.close()

        print ("Scan Number",ScanNum)


        FileName = 'Scan'+ScanNum+'_PH.dat'

        #Read Inlet Line
        rS_top=(',iE(set),iE(read),YF(set),YF(read),YB(set),YB(read),EE(set),EE(read),IR(set),IR(read),TV(set),TV(read),FC(set),FC(read),FV(set),FV(read),TC(set),TC(read),EC(set),EC(read)')
        foInitial = open(FileName,"a")
        foInitial.write("iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4"+rS_top+"\n")

        foInitial.close()

        foRun = open(FileName,"a")
        #Collected data
        for x in range (0, len(iE)):

            outputString=(str(iE[x])+","+str(L5[x])+","+
                          str(L4[x])+","+str(L3[x])+","+
                          str(L2[x])+","+str(L1[x])+","+
                          str(Ax[x])+","+str(H1[x])+","+
                          str(H2[x])+","+str(H3[x])+","+str(H4[x])+rS_[x])
            
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
 #       print ("N", N)
        if (N>0):
            p=GraphFrame.plot()
##        else:
##            print ("iE off")

  
class Controls(tk.Frame):
    
    def __init__(self, root):
        tk.Frame.__init__(self, root)

    def callback(*args):
    #    print ("variable changed!")
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

    FS_checked = tk.IntVar()
    FS_checked.trace("w", callback)
    FS_checked.set(0)

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
    c11=tk.Checkbutton(root, text="Fast Scan", onvalue=1, offvalue=0, variable=FS_checked)
    
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
    c11.pack(side="left", fill="x")
        
# root window created. Here, that would be the only window, but
# you can later have windows within windows.

root.geometry("800x600")

#creation of an instance
graph = GraphFrame(root)
controls=Controls(root)

graph.pack(side="left", fill="x")
controls.pack(side="bottom", fill="x")

#mainloop 
root.mainloop()
