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
import threading


matplotlib.use("TkAgg")

N=0
root = tk.Tk()

frame1 = tk.Frame(root, borderwidth=10)
fig = plt.Figure(figsize=(6,4),dpi=100)
canvas = FigureCanvasTkAgg(fig, frame1)
#canvas.get_tk_widget().pack(side="left", fill="x")
ax = fig.add_subplot(111)
toolbar = NavigationToolbar2Tk(canvas, frame1)
toolbar.update()
frame1.pack(side=tk.LEFT, fill=tk.X)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.X)

frame2=tk.Frame(root, width=400, height=400, colormap="new", borderwidth=10)
frame2.pack(side=tk.RIGHT, fill=tk.X)

AqTime = tk.IntVar()
scanOp = tk.IntVar()


        
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

        scan = tk.Menu(menu)
        scan.add_command(label="Run", command=self.RunScan)
        scan.add_command(label="Exit", command=self.exit)
        menu.add_cascade(label="Scan", menu=scan)
        
        data = tk.Menu(menu)
        data.add_command(label="Open File", command=self.openFile)
        menu.add_cascade(label="Data", menu=data)
        
        settings = tk.Menu(menu)
        #settings.add_command(label="Acq Time")
        aqutime = tk.Menu(settings)
        settings.add_cascade(label="Acq Time", menu=aqutime)

        
        
        aqutime.add_radiobutton(label='100ms', value=100, variable=AqTime)
        aqutime.add_radiobutton(label='200ms', value=200, variable=AqTime)
        aqutime.add_radiobutton(label='300ms', value=300, variable=AqTime)
        aqutime.add_radiobutton(label='400ms', value=400, variable=AqTime)
        aqutime.add_radiobutton(label='500ms', value=500, variable=AqTime)
        aqutime.add_radiobutton(label='600ms', value=600, variable=AqTime)
        aqutime.add_radiobutton(label='700ms', value=700, variable=AqTime)
        aqutime.add_radiobutton(label='800ms', value=800, variable=AqTime)
        aqutime.add_radiobutton(label='900ms', value=900, variable=AqTime)
        aqutime.add_radiobutton(label='1000ms', value=1000, variable=AqTime)

        AqTime.set(100)

        ScanOption = tk.Menu(settings)
        settings.add_cascade(label="Secondary Scan", menu=ScanOption)

        ScanOption.add_radiobutton(label='None', value=1, variable=scanOp)
        ScanOption.add_radiobutton(label='Y-Focus', value=2, variable=scanOp)
        ScanOption.add_radiobutton(label='Y-Bias', value=3, variable=scanOp)
        ScanOption.add_radiobutton(label='Electron Energy', value=4, variable=scanOp)
        ScanOption.add_radiobutton(label='Ion Repellar', value=5, variable=scanOp)

        scanOp.set(1)

        menu.add_cascade(label="Settings", menu=settings)
        
   #     mb_radmenu = tk.Menu(menu)
   #     menu.configure(menu=mb_radmenu)

        

        #Check to see if the Mass Spec is attached.
        #If it isn't, will need to run in offline mode.
##        print ("Attempting to connect to mass spec")
##        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##        s.settimeout(10)
##        try: 
##            print (s.recv(1024).decode("utf-8"))
##            s.connect(('localhost',1090))
##        except socket.error as e:
##            print(e)
##        s.close()
        Controls.ReadMassSpec()

           
    def exit(self):
        print(AqTime.get())
        exit()

    def RunScan(self):

        #acqTime=100
        acqTime=AqTime.get()
        acqRestTime=0.2+(acqTime/1000)
        acqAStr=("SetAcqPeriod "+str(acqTime)+"\r\n")

        print(acqRestTime)
        
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
        s.send(b'SetSourceOutput IE,1300.0000\r\n')
        time.sleep(0.2)
        Dummy=(s.recv(1024).decode("utf-8"))
        s.send(str.encode(acqAStr))
        time.sleep(0.2)
        
        #s.send(b'SetAcqPeriod 100\r\n')
        
        Dummy= ("SetAcqPeriod",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))

        #print (Dummy)
        
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
        total_scans=1

        while scans < total_scans:
            SV=1450.000
            TV=1550.000
            StepSize=1

            print ("Initialise Source Voltage")
            s.send(b'SetSourceOutput IE,1450.0000\r\n')
           # time.sleep(60)
            Dummy=(s.recv(1024).decode("utf-8"))

            print ("Scans Number",scans+1)
            

            while SV < TV:
                print ("Scan Number",scans,"Voltage",SV)

                #Set Source Voltage
##                BStr=("SetSourceOutput IE,")
##                CStr=(str(SV)+"\r\n")
##                AStr=BStr+CStr
##                s.send(str.encode(AStr))
                
                SVStr=("SetSourceOutput IE,"+str(SV)+"\r\n")
                s.send(str.encode(SVStr))

                time.sleep(0.1)
                IEreturn=(s.recv(1024))
                time.sleep(0.1)
                
                #Acquire Data - waitfor enough time for the buffer to fill....
                s.send(b'StartAcq 1,JS\r\n')
                time.sleep(acqRestTime)
                returnString=s.recv(1024)
                time.sleep(0.1)

                #Get the Isotopx voltages (unless running a fast scan)
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
                rS=(str(SV)+","+spec)
                rS=rS[0:-5]
                spectrum=rS.split(',')

                print (spectrum)

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


                
                SV=SV+StepSize

            s.send(b'SetSourceOutput IE,1450.0000\r\n')
            time.sleep(0.2)
            print (s.recv(1024))    
            

            self.outputData(iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4,rS_)

            

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
        

    def openFile(self):
        global spectrum
        #Open file to read spectrum
        root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("dat files","*.dat"),("all files","*.*")))

        try:
            spectrum=np.genfromtxt(root.filename,delimiter=',', invalid_raise = False, names=True)
        except Warning as e:
           print (e)

        self.channelConv()

    def channelConv(self):
        j=0
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
         
        while j<len(spectrum):
            dataLine=spectrum[j]
            dataString=str(dataLine)
            dataLine=(dataString[1:-1])
            splitString=dataLine.split(',')
            
            iE_.append(float(splitString[0]))
            L5_.append(float(splitString[1]))
            L4_.append(float(splitString[2]))
            L3_.append(float(splitString[3]))
            L2_.append(float(splitString[4]))
            L1_.append(float(splitString[5]))
            Ax_.append(float(splitString[6]))
            H1_.append(float(splitString[7]))
            H2_.append(float(splitString[8]))
            H3_.append(float(splitString[9]))
            H4_.append(float(splitString[10]))
        
            j=j+1
        #Make the channels global
            
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

    def outputData(self, iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4,rS_):
        print("Output Data to File")

        os.chdir("c:\\MSSData")

        file_to_open = "ScanNum.txt"
        #print (file_to_open)

        #Get current helium run number
        fo = open(file_to_open, "r")
        ScanNum = fo.readline()
        fo.close()

        print ("Scan Number",ScanNum)


        FileName = 'Scan'+ScanNum+'.dat'

        #Read Inlet Line
        rS_top=('iE(set),iE(read),YF(set),YF(read),YB(set),YB(read),EE(set),EE(read),IR(set),IR(read),TV(set),TV(read),FC(set),FC(read),FV(set),FV(read),TC(set),TC(read),EC(set),EC(read)')
        foInitial = open(FileName,"a")
        foInitial.write("iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4,"+rS_top+"\n")

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
        if (N>0):
            p=GraphFrame.plot()

class Controls(tk.Frame):
    
    def __init__(self, root):
        tk.Frame.__init__(self, root)

    def callback(*args):
        GraphFrame.UpdatePlot()

    def ReadMassSpec():
        #Read the mass spec
        print ("Reading mass Spec")
        print ("Connecting to mass spec")
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            #Connect to instrument

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

            #Get readbacks of voltages
            sleepyTime=0.1
            s.send(b'GSO IE\r\n')
            time.sleep(sleepyTime)
            rS_IE=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_IE = rS_IE.replace('\n', ' ').replace('\r', '')
            splitString=rS_IE.split(',')
            Controls.iERead.delete(0,tk.END)
            Controls.iERead.insert(1,splitString[1])

            
            s.send(b'GSO YF\r\n')
            time.sleep(sleepyTime)
            rS_YF=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_YF = rS_YF.replace('\n', ' ').replace('\r', '')
            splitString=rS_YF.split(',')
            Controls.yFRead.delete(0,tk.END)
            Controls.yFRead.insert(1,splitString[1])

            s.send(b'GSO YB\r\n')
            time.sleep(sleepyTime)
            rS_YB=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_YB = rS_YB.replace('\n', ' ').replace('\r', '')
            splitString=rS_YB.split(',')
            Controls.yBRead.delete(0,tk.END)
            Controls.yBRead.insert(1,splitString[1])      

            s.send(b'GSO EE\r\n')
            time.sleep(sleepyTime)
            rS_EE=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_EE = rS_EE.replace('\n', ' ').replace('\r', '')
            splitString=rS_EE.split(',')
            Controls.EERead.delete(0,tk.END)
            Controls.EERead.insert(1,splitString[1])        

            s.send(b'GSO IR\r\n')
            time.sleep(sleepyTime)
            rS_IR=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_IR = rS_IR.replace('\n', ' ').replace('\r', '')
            splitString=rS_IR.split(',')
            Controls.IRRead.delete(0,tk.END)
            Controls.IRRead.insert(1,splitString[1])

            s.send(b'GSO TV\r\n')
            time.sleep(sleepyTime)
            rS_TV=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_TV = rS_TV.replace('\n', ' ').replace('\r', '')
            splitString=rS_TV.split(',')
            Controls.TVRead.delete(0,tk.END)
            Controls.TVRead.insert(1,splitString[1])

            s.send(b'GSO FC\r\n')
            time.sleep(sleepyTime)
            rS_FC=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_FC = rS_FC.replace('\n', ' ').replace('\r', '')
            splitString=rS_FC.split(',')
            Controls.FCRead.delete(0,tk.END)
            Controls.FCRead.insert(1,splitString[1])

            s.send(b'GSO FV\r\n')
            time.sleep(sleepyTime)
            rS_FV=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_FV = rS_FV.replace('\n', ' ').replace('\r', '')
            splitString=rS_FV.split(',')
            Controls.FVRead.delete(0,tk.END)
            Controls.FVRead.insert(1,splitString[1])

            s.send(b'GSO TC\r\n')
            time.sleep(sleepyTime)
            rS_TC=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_TC = rS_TC.replace('\n', ' ').replace('\r', '')
            splitString=rS_TC.split(',')
            Controls.TCRead.delete(0,tk.END)
            Controls.TCRead.insert(1,splitString[1])         

            s.send(b'GSO EC\r\n')
            time.sleep(sleepyTime)
            rS_EC=s.recv(1024).decode("utf-8")
            time.sleep(sleepyTime)
            rS_EC = rS_EC.replace('\n', ' ').replace('\r', '')
            splitString=rS_EC.split(',')
            Controls.ECRead.delete(0,tk.END)
            Controls.ECRead.insert(1,splitString[1])
            
            s.close()

        except socket.error as e:
            print ("Error: ",e)


        


    #FRAME FOR SETTINGS (ION ENERGY ETC)
    TopRow=tk.Frame(frame2)
    lblLbl = tk.Label(TopRow, text="  ",width=8,anchor='w')
    lblLbl.pack(side=tk.LEFT)
    lblFrom = tk.Label(TopRow, text="From",width=8,anchor='w')
    lblFrom.pack(side=tk.LEFT)
    lblTo = tk.Label(TopRow, text=" To",width=6,anchor='w')
    lblTo.pack(side=tk.LEFT)
    lblRead = tk.Button(TopRow, text="Read", width=6, command=ReadMassSpec)
    lblRead.pack(side=tk.LEFT)
    
    TopRow.pack(side=tk.TOP, fill=tk.NONE)
    #Ion Energy
    iEFrame=tk.Frame(frame2)
    iElbl = tk.Label(iEFrame, text="iE",width=5,anchor='w')
    iElbl.pack(side=tk.LEFT)
    iEFrom = tk.Entry(iEFrame,width=8)
    iEFrom.pack(side="left",padx=5)
    iETo = tk.Entry(iEFrame,width=8)
    iETo.pack(side="left",padx=5)
    iERead = tk.Entry(iEFrame,width=8)
    iERead.pack(side="left",padx=5)
    iEFrame.pack(side=tk.TOP, fill=tk.NONE)
    #YFocus
    YFframe=tk.Frame(frame2)
    yFlbl = tk.Label(YFframe, text="YF",width=5,anchor='w')
    yFlbl.pack(side=tk.LEFT)
    yFFrom = tk.Entry(YFframe,width=8)
    yFFrom.pack(side="left",padx=5)
    yFTo = tk.Entry(YFframe,width=8)
    yFTo.pack(side="left",padx=5)
    yFRead = tk.Entry(YFframe,width=8)
    yFRead.pack(side="left",padx=5)
    YFframe.pack(side=tk.TOP, fill=tk.NONE)
    #YBias
    YBframe=tk.Frame(frame2)
    yBlbl = tk.Label(YBframe, text="YB",width=5,anchor='w')
    yBlbl.pack(side=tk.LEFT)
    yBFrom = tk.Entry(YBframe,width=8)
    yBFrom.pack(side="left",padx=5)
    yBTo = tk.Entry(YBframe,width=8)
    yBTo.pack(side="left",padx=5)
    yBRead = tk.Entry(YBframe,width=8)
    yBRead.pack(side="left",padx=5)
    YBframe.pack(side=tk.TOP, fill=tk.NONE)
    #Electron Energy
    EEframe=tk.Frame(frame2)
    EElbl = tk.Label(EEframe, text="EE",width=5,anchor='w')
    EElbl.pack(side=tk.LEFT)
    EEFrom = tk.Entry(EEframe,width=8)
    EEFrom.pack(side="left",padx=5)
    EETo = tk.Entry(EEframe,width=8)
    EETo.pack(side="left",padx=5)
    EERead = tk.Entry(EEframe,width=8)
    EERead.pack(side="left",padx=5)
    EEframe.pack(side=tk.TOP, fill=tk.NONE)
    #Ion repeller
    IRframe=tk.Frame(frame2)
    IRlbl = tk.Label(IRframe, text="IR",width=5,anchor='w')
    IRlbl.pack(side=tk.LEFT)
    IRFrom = tk.Entry(IRframe,width=8)
    IRFrom.pack(side="left",padx=5)
    IRTo = tk.Entry(IRframe,width=8)
    IRTo.pack(side="left",padx=5)
    IRRead = tk.Entry(IRframe,width=8)
    IRRead.pack(side="left",padx=5)
    IRframe.pack(side=tk.TOP, fill=tk.NONE)
    #Trap Voltage
    TVframe=tk.Frame(frame2)
    TVlbl = tk.Label(TVframe, text="TV",width=5,anchor='w')
    TVlbl.pack(side=tk.LEFT)
    TVFrom = tk.Entry(TVframe,width=8)
    TVFrom.pack(side="left",padx=5)
    TVTo = tk.Label(TVframe, text="",width=8)
    TVTo.pack(side="left",padx=0)
    TVRead = tk.Entry(TVframe,width=8)
    TVRead.pack(side="left",padx=5)
    TVframe.pack(side=tk.TOP, fill=tk.NONE)        
    #Filament Current
    FCframe=tk.Frame(frame2)
    FClbl = tk.Label(FCframe, text="FC",width=5,anchor='w')
    FClbl.pack(side=tk.LEFT)
    FCFrom = tk.Label(FCframe, text="",width=8)
    FCFrom.pack(side="left",padx=0)
    FCTo =  tk.Label(FCframe, text="",width=8)
    FCTo.pack(side="left",padx=0)
    FCRead = tk.Entry(FCframe,width=8)
    FCRead.pack(side="left",padx=5)
    FCframe.pack(side=tk.TOP, fill=tk.NONE)     
    #Filament Voltage
    FVframe=tk.Frame(frame2)
    FVlbl = tk.Label(FVframe, text="FV",width=5,anchor='w')
    FVlbl.pack(side=tk.LEFT)
    FVFrom = tk.Entry(FVframe,width=8)
    FVFrom.pack(side="left",padx=5)
    FVTo = tk.Label(FVframe, text="",width=8)
    FVTo.pack(side="left",padx=0)
    FVRead = tk.Entry(FVframe,width=8)
    FVRead.pack(side="left",padx=5)
    FVframe.pack(side=tk.TOP, fill=tk.NONE)    
    #Trap Current
    TCframe=tk.Frame(frame2)
    TClbl = tk.Label(TCframe, text="TC",width=5,anchor='w')
    TClbl.pack(side=tk.LEFT)
    TCFrom = tk.Label(TCframe, text="",width=8)
    TCFrom.pack(side="left",padx=0)
    TCTo = tk.Label(TCframe, text="",width=8)
    TCTo.pack(side="left",padx=0)
    TCRead = tk.Entry(TCframe,width=8)
    TCRead.pack(side="left",padx=5)
    TCframe.pack(side=tk.TOP, fill=tk.NONE)    
    #Emission Current
    ECframe=tk.Frame(frame2)
    EClbl = tk.Label(ECframe, text="EC",width=5,anchor='w')
    EClbl.pack(side=tk.LEFT)
    ECFrom = tk.Label(ECframe, text="",width=8)
    ECFrom.pack(side="left",padx=0)
    ECTo = tk.Label(ECframe, text="",width=8)
    ECTo.pack(side="left",padx=0)
    ECRead = tk.Entry(ECframe,width=8)
    ECRead.pack(side="left",padx=5)
    ECframe.pack(side=tk.TOP, fill=tk.NONE)     
    #Channels
    CHframe=tk.Frame(frame2)
    CHlbl = tk.Label(CHframe, text="Channels",width=20)
    CHlbl.pack(side=tk.LEFT)
    CHframe.pack(side=tk.TOP, fill=tk.NONE)     

 

    
    CtrlFrame1= tk.Frame(frame2)
    CtrlFrame2= tk.Frame(frame2)
    CtrlFrame3= tk.Frame(frame2)   

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
    FS_checked.set(1)
    
    c1=tk.Checkbutton(CtrlFrame1, text="L5", onvalue=1, offvalue=0, variable=L5_checked)
    c2=tk.Checkbutton(CtrlFrame1, text="L4", onvalue=1, offvalue=0, variable=L4_checked)
    c3=tk.Checkbutton(CtrlFrame1, text="L3", onvalue=1, offvalue=0, variable=L3_checked)
    c4=tk.Checkbutton(CtrlFrame1, text="L2", onvalue=1, offvalue=0, variable=L2_checked)
    c5=tk.Checkbutton(CtrlFrame1, text="L1", onvalue=1, offvalue=0, variable=L1_checked)
    c6=tk.Checkbutton(CtrlFrame2, text="Ax", onvalue=1, offvalue=0, variable=Ax_checked)
    c7=tk.Checkbutton(CtrlFrame2, text="H1", onvalue=1, offvalue=0, variable=H1_checked)
    c8=tk.Checkbutton(CtrlFrame2, text="H2", onvalue=1, offvalue=0, variable=H2_checked)
    c9=tk.Checkbutton(CtrlFrame2, text="H3", onvalue=1, offvalue=0, variable=H3_checked)
    c10=tk.Checkbutton(CtrlFrame2, text="H4", onvalue=1, offvalue=0, variable=H4_checked)
    c11=tk.Checkbutton(CtrlFrame3, text="Fast Scan", onvalue=1, offvalue=0, variable=FS_checked)
    
    c1.pack(side="left", fill="both")
    c2.pack(side="left", fill="both")
    c3.pack(side="left", fill="both")
    c4.pack(side="left", fill="both")
    c5.pack(side="left", fill="both")
    c6.pack(side="left", fill="both")
    c7.pack(side="left", fill="both")
    c8.pack(side="left", fill="both")
    c9.pack(side="left", fill="both")
    c10.pack(side="left", fill="both")
    c11.pack(side="right", fill="both")

    

    b = tk.Button(CtrlFrame3, text="OK", command=callback)
    b.pack()

    

    
    CtrlFrame1.pack(side=tk.TOP, fill=tk.NONE,pady=3)
    CtrlFrame2.pack(side=tk.TOP, fill=tk.NONE,pady=3)
    CtrlFrame3.pack(side=tk.TOP, fill=tk.NONE,pady=5)
    

        
# root window created. Here, that would be the only window, but
# you can later have windows within windows.

root.geometry("900x600")

#creation of an instance
graph = GraphFrame(root)
controls=Controls(root)

graph.pack(side="left", fill="x")
controls.pack(side="right", fill="both")

#mainloop 
root.mainloop()
