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
from tkinter import ttk
from tkinter import messagebox


matplotlib.use("TkAgg")

root = tk.Tk()
frame1 = tk.Frame(root, borderwidth=10)
fig = plt.Figure(figsize=(6,4),dpi=100)
canvas = FigureCanvasTkAgg(fig, frame1)
ax = fig.add_subplot(111)
frame3 = tk.Frame(root, borderwidth=10)
frame3.pack(side=tk.TOP, fill=tk.BOTH)
toolbar = NavigationToolbar2Tk(canvas, frame1)
toolbar.update()
frame1.pack(side=tk.LEFT, fill=tk.X)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.X)
frame2=tk.Frame(root, width=400, height=400, colormap="new", borderwidth=10)
frame2.pack(side=tk.RIGHT, fill=tk.X)


#Enter globals here

N=0
AqTime = tk.IntVar()
integrations = tk.IntVar()
PTSItem=[]



############################
# Left hand frame functions
############################
        
class GraphFrame(tk.Frame):

    def __init__(self, master=None):
        
        tk.Frame.__init__(self, master)   
        self.master = master
        self.init_window()
        
    def init_window(self):
        
        self.master.title("Python Mass Spectrometer Controller (Peakhopping version)")
        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.NONE)

        #Create the menus
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
        settings.add_command(label="Load Settings",command=self.LoadSettings)
        aqutime = tk.Menu(settings)
        settings.add_cascade(label="Acquisition Time", menu=aqutime)

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

        Integrations= tk.Menu(settings)
        settings.add_cascade(label="Integrations", menu=Integrations)

        Integrations.add_radiobutton(label='1', value=1, variable=integrations)
        Integrations.add_radiobutton(label='2', value=2, variable=integrations)
        Integrations.add_radiobutton(label='3', value=3, variable=integrations)
        Integrations.add_radiobutton(label='4', value=4, variable=integrations)
        Integrations.add_radiobutton(label='5', value=5, variable=integrations)
        Integrations.add_radiobutton(label='6', value=6, variable=integrations)
        Integrations.add_radiobutton(label='7', value=7, variable=integrations)
        Integrations.add_radiobutton(label='8', value=8, variable=integrations)
        Integrations.add_radiobutton(label='9', value=9, variable=integrations)
        Integrations.add_radiobutton(label='10', value=10, variable=integrations)

        integrations.set(1)

        menu.add_cascade(label="Settings", menu=settings)

        #Read the Mass Spec and update the "Read" column
        Controls.ReadMassSpec()

           
    def exit(self):
        exit()

    def LoadSettings(self):
        #Load the settings from file
        root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("dat files","*.dat"),("all files","*.*")))

        try:
            settings=np.genfromtxt(root.filename,delimiter=',', invalid_raise = False, names=True)
        except filedialog.EXCEPTION as e:
           print (e)
           return None
           
        #Ion Energy
        dataLine=settings[0]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.iEFrom.delete(0,tk.END)
        Controls.iEFrom.insert(1,splitString[0])       
        #Y Focus
        dataLine=settings[1]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.yFFrom.delete(0,tk.END)
        Controls.yFFrom.insert(1,splitString[0])       
        #Y Bias
        dataLine=settings[2]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.yBFrom.delete(0,tk.END)
        Controls.yBFrom.insert(1,splitString[0])       
        #Electron Energy
        dataLine=settings[3]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.EEFrom.delete(0,tk.END)
        Controls.EEFrom.insert(1,splitString[0])       
        #Ion Repeller
        dataLine=settings[4]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.IRFrom.delete(0,tk.END)
        Controls.IRFrom.insert(1,splitString[0])       
        #Trap Voltage
        dataLine=settings[5]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.TVFrom.delete(0,tk.END)
        Controls.TVFrom.insert(1,splitString[0])       
        #Trap Current
        dataLine=settings[6]
        dataString=str(dataLine)
        SettingsLine=(dataString[1:-1])
        splitString=SettingsLine.split(',')
        Controls.TCFrom.delete(0,tk.END)
        Controls.TCFrom.insert(1,splitString[0])

               
    def RunScan(self):

        #Check that there is a valid IE range
        if (len(PTSItem)==0):
            tk.messagebox.showerror("Error", "No peaks to scan")

            return None
            
        #Check to see if a fast or slow scan is being run
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

        try:
            s.connect(('localhost',1090))
            print (s.recv(1024).decode("utf-8"))
        except socket.error as e:
            print (e)
            print ("Exiting")
            return None

        #If connection was successful, log in.
        print ("Logging In to Mass Spec...")
        #Login
        s.send(b'login i,pw \r\n')
        time.sleep(0.2)
        print (s.recv(1024).decode("utf-8"))
        time.sleep(0.2)
        s.send(b'ver\r\n')
        time.sleep(0.2)
        print ("Version"+s.recv(1024).decode("utf-8"))

        #Set the aquisition period and rest time (based on single integration)
        acqTime=AqTime.get()
        acqAStr=("SetAcqPeriod "+str(acqTime)+"\r\n")
        s.send(str.encode(acqAStr))
        time.sleep(0.2)
        Dummy= ("SetAcqPeriod",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        acqRestTime=0.2+(acqTime/1000)
    
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

        #Get Number of Integrations from menu
        AquIntTimeInt=integrations.get()        
        
        print ("Start Scan")
        #How many peaks to scan
        N_PTS=len(PTSItem)

        print(N_PTS)

        StartPoint=0
        EndPoint=N_PTS

 
        
        while (StartPoint<EndPoint):

            #To avoid charging issues, for now, sit at 1000V between scans
            print ("1000V")
            SVStr=("SetSourceOutput IE, 1000 \r\n")
            s.send(str.encode(SVStr))
            time.sleep(0.1)
            IEreturn=(s.recv(1024))
            time.sleep(30)
            print ("Start scan")

            print ("Item ",PTSItem[StartPoint])

            SV=float(PTSItem[StartPoint])

            #Set the voltage
            SVStr=("SetSourceOutput IE,"+str(SV)+"\r\n")
            s.send(str.encode(SVStr))
            time.sleep(0.1)
            IEreturn=(s.recv(1024))
            time.sleep(0.1)

            #Load the current settings into float values
            #to populate the fast scan arrays

            fltYF=float(Controls.yFFrom.get())
            fltYB=float(Controls.yBFrom.get())
            fltEE=float(Controls.EEFrom.get())
            fltIR=float(Controls.IRFrom.get())
            fltTV=float(Controls.TVFrom.get())
            fltFV=float(Controls.FVRead.get())

            #Do N scans

            N_scans=30
            N_init=0
            
            while N_init < N_scans:
                
                #Acquire Data - wait for enough time for the buffer to fill....
                AcqCommandToSend=('StartAcq '+ str(AquIntTimeInt)+',JS\r\n')
                s.send(str.encode(AcqCommandToSend))
                
                #s.send(b'StartAcq 1,JS\r\n')
                time.sleep((1*AquIntTimeInt*acqRestTime))
                returnString=s.recv(4096)
                time.sleep(0.1)

##                AcqStop=('StopAcq \r\n')
##                s.send(str.encode(AcqCommandToSend))
##                returnedStop=s.recv(1024).decode("utf-8")
##                print(N_init, returnedStop)

                

                #Get the voltages (unless running a fast scan)
                #If running a fast scan, then the settings from the settings
                #box on the GUI can go in the first column
                if FastScan:
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

                    rS_TV=(str(fltTV)+",0")
                    rS_FC=("0,0")
                    rS_FV=(str(fltFV)+",0")
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
                #print(spec)

                
                tempStr=spec.split('#')
                
                temp_i=1
                data_N=0
                SpecIntegration=[]
                StringStart=""
                while (temp_i<len(tempStr)):
                    

                    SpecIntegration.append(tempStr[temp_i])


                    data_N=data_N+1
                    temp_i=temp_i+2


                
                
                tempStr2=tempStr[1].split(',')

                StringStart=(tempStr2[0]+','+
                             tempStr2[1]+','+
                             tempStr2[2]+','+
                             tempStr2[3]+','+
                             tempStr2[4]+',')
                

                temp_col=5
                averagedData=[]
                #Loop through the columns and integrations to
                #average out the data.
                #Currently just the average (no std dev) is used.

                #Loop through channels
                while (temp_col<16):
                    running=0.0
                    data_N=0
                    
                    #Loop through integrations
                    while (data_N<len(SpecIntegration)):
                        dummyString=SpecIntegration[data_N].split(',')
                        running=running+float(dummyString[temp_col])
                        data_N=data_N+1
                    
                    running=running/len(SpecIntegration)
                    averagedData.append(running)
                    temp_col=temp_col+1
                    



                #Add the averaged data to a string.
                temp_i=0
                EndString=""
                while (temp_i<len(averagedData)):

                       EndString=(EndString+str(averagedData[temp_i])+',')
                       temp_i=temp_i+1

                EndString=EndString[:-1]


                #Reform the data string to match that created by the mass
                #spec acquisition return
                spec2='#'+StringStart+EndString+'#'
                
                #Add the Ion Source voltage to the start of the string
                rS=(str(SV)+","+spec2)
                rS=rS[0:-1]
                spectrum=rS.split(',')

                #print (spectrum)
                #Add the inidividual readings to the relevent array
                #for data output and plotting
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
                H3_.append(float(spectrum[15]))
                H4_.append(float(spectrum[15]))
         
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
               
                #Plot
                p=GraphFrame.plot()

                #Increase Source Voltage                
                N_init=N_init+1

            #Increment the "Secondary Increment"
            StartPoint=StartPoint+1

        print ("set to 1000V")
        SVStr=("SetSourceOutput IE, 1000 \r\n")
        s.send(str.encode(SVStr))
        time.sleep(0.1)
        IEreturn=(s.recv(1024))

        s.close()
        #Output the data to file
        self.outputData(iE,L5,L4,L3,L2,L1,Ax,H1,H2,H3,H4,rS_)          

        #Reset Arrays
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
        

    def openFile(self):
        global spectrum
        #Open file to read spectrum
        root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("dat files","*.dat"),("all files","*.*")))

        try:
            spectrum=np.genfromtxt(root.filename,delimiter=',', invalid_raise = False, names=True)
        except Warning as e:
           print (e)
           return None
    
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


        FileName = 'Scan'+ScanNum+'_PH.dat'

        #Read Inlet Line
        rS_top=('iE(set),iE(read),YF(set),YF(read),YB(set),YB(read),EE(set),EE(read),IR(set),IR(read),TV(set),TV(read),FC(set),FC(read),FV(set),FV(read),TC(set),TC(read),EC(set),EC(read),')
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
            #ax.plot(iE,L5,color='green')
            ax.scatter(iE,L5,color='green')
        
        if Controls.L4_checked.get():
            ax.scatter(iE,L4,color='red')

        if Controls.L3_checked.get():
            ax.scatter(iE,L3,color='blue')

        if Controls.L2_checked.get():
            ax.scatter(iE,L2,color='cyan')

        if Controls.L1_checked.get():
            ax.scatter(iE,L1,color='yellow')

        if Controls.Ax_checked.get():
            ax.scatter(iE,Ax,color='magenta')            

        if Controls.H1_checked.get():
            ax.scatter(iE,H1,color='black')

        if Controls.H2_checked.get():
            ax.scatter(iE,H2,color='0.25')              

        if Controls.H3_checked.get():
            ax.scatter(iE,H3,color='0.5')  

        if Controls.H4_checked.get():
            ax.scatter(iE,H4,color='0.75')

        fig.canvas.draw_idle()
        root.update()
        return 1

    def UpdatePlot():
        #Check to see if a scan is loaded. If iE is empty then dont call the plot
        if (N>0):
            p=GraphFrame.plot()

############################
# Right Hand Frame functions
############################

class Controls(tk.Frame):
    
    def __init__(self, root):
        tk.Frame.__init__(self, root)

    def callback(*args):
        GraphFrame.UpdatePlot()

    def TestDef():
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)

        try:
            #Connect to instrument

            s.connect(('localhost',1090))
            print (s.recv(1024).decode("utf-8"))

        except socket.error as e:
            print ("Error: ",e)
            Controls.StatusUpdate("Offline")
            return None
            
        #Login
        Controls.StatusUpdate("Logging In")
        s.send(b'login i,pw \r\n')
        time.sleep(0.2)
        print (s.recv(1024).decode("utf-8"))
        time.sleep(0.2)
        s.send(b'ver\r\n')
        time.sleep(0.2)
        print ("Version"+s.recv(1024).decode("utf-8"))
        
        s.send(b'SFCM trap\r\n')
        time.sleep(0.2)
        print ("Filament Control mode: "+s.recv(1024).decode("utf-8"))

        s.send(b'SSO TC,150\r\n')
        time.sleep(0.2)
        print ("Trap Current Set: "+s.recv(1024).decode("utf-8"))
        
        s.send(b'GFCM \r\n')
        time.sleep(0.2)
        GFCM=s.recv(1024).decode("utf-8")
        time.sleep(0.2)

        print (GFCM)        


        
        s.close()


        


    def StatusUpdate(StatusText):
        #Update the status bar with any messages
        Controls.StatusLbl.config(text=StatusText)
        
        
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

        except socket.error as e:
            print ("Error: ",e)
            tk.messagebox.showwarning("Warning", "Mass Spec Not Connected")
            Controls.StatusUpdate("Offline")
            return None
            
        #Login
        Controls.StatusUpdate("Logging In")
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
        Controls.iEFrom.delete(0,tk.END)
        Controls.iEFrom.insert(1,splitString[0])   
            
        s.send(b'GSO YF\r\n')
        time.sleep(sleepyTime)
        rS_YF=s.recv(1024).decode("utf-8")
        time.sleep(sleepyTime)
        rS_YF = rS_YF.replace('\n', ' ').replace('\r', '')
        splitString=rS_YF.split(',')
        Controls.yFRead.delete(0,tk.END)
        Controls.yFRead.insert(1,splitString[1])
        Controls.yFFrom.delete(0,tk.END)
        Controls.yFFrom.insert(1,splitString[0])  

        s.send(b'GSO YB\r\n')
        time.sleep(sleepyTime)
        rS_YB=s.recv(1024).decode("utf-8")
        time.sleep(sleepyTime)
        rS_YB = rS_YB.replace('\n', ' ').replace('\r', '')
        splitString=rS_YB.split(',')
        Controls.yBRead.delete(0,tk.END)
        Controls.yBRead.insert(1,splitString[1])      
        Controls.yBFrom.delete(0,tk.END)
        Controls.yBFrom.insert(1,splitString[0])
        
        s.send(b'GSO EE\r\n')
        time.sleep(sleepyTime)
        rS_EE=s.recv(1024).decode("utf-8")
        time.sleep(sleepyTime)
        rS_EE = rS_EE.replace('\n', ' ').replace('\r', '')
        splitString=rS_EE.split(',')
        Controls.EERead.delete(0,tk.END)
        Controls.EERead.insert(1,splitString[1])
        Controls.EEFrom.delete(0,tk.END)
        Controls.EEFrom.insert(1,splitString[0])   

        s.send(b'GSO IR\r\n')
        time.sleep(sleepyTime)
        rS_IR=s.recv(1024).decode("utf-8")
        time.sleep(sleepyTime)
        rS_IR = rS_IR.replace('\n', ' ').replace('\r', '')
        splitString=rS_IR.split(',')
        Controls.IRRead.delete(0,tk.END)
        Controls.IRRead.insert(1,splitString[1])
        Controls.IRFrom.delete(0,tk.END)
        Controls.IRFrom.insert(1,splitString[0])
        
        s.send(b'GSO TV\r\n')
        time.sleep(sleepyTime)
        rS_TV=s.recv(1024).decode("utf-8")
        time.sleep(sleepyTime)
        rS_TV = rS_TV.replace('\n', ' ').replace('\r', '')
        splitString=rS_TV.split(',')
        Controls.TVRead.delete(0,tk.END)
        Controls.TVRead.insert(1,splitString[1])
        Controls.TVFrom.delete(0,tk.END)
        Controls.TVFrom.insert(1,splitString[0])
        
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

        Controls.StatusUpdate("Voltages Read")
        
        s.close()

    def SetMassSpec():
        #Read the mass spec
        print ("Sending settings to mass Spec")
        print ("Connecting to mass spec")
        Controls.StatusUpdate("Connecting to Mass Spec")
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            #Connect to instrument

            s.connect(('localhost',1090))
            print (s.recv(1024).decode("utf-8"))

        except socket.error as e:
            Controls.StatusUpdate("Offline")
            print ("Error: ",e)
            return None
            
        #Login
        Controls.StatusUpdate("Logging In")
        s.send(b'login i,pw \r\n')
        time.sleep(0.2)
        print (s.recv(1024).decode("utf-8"))
        time.sleep(0.2)
        s.send(b'ver\r\n')
        time.sleep(0.2)
        print ("Version"+s.recv(1024).decode("utf-8"))


        #Set variables
        #Ion Energy
        SV=float(Controls.iEFrom.get())
        SVStr=("SetSourceOutput IE,"+str(SV)+"\r\n")
        s.send(str.encode(SVStr))
        Dummy= ("Source Voltage: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        print (Dummy)
        time.sleep(0.5)
        #Y Focus
        YF=float(Controls.yFFrom.get())
        YFStr=("SetSourceOutput YF,"+str(YF)+"\r\n")
        s.send(str.encode(YFStr))
        Dummy= ("Y-Focus: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        print (Dummy)
        time.sleep(0.5)
        #Y Bias
        YB=float(Controls.yBFrom.get())
        YBStr=("SetSourceOutput YB,"+str(YB)+"\r\n")
        s.send(str.encode(YBStr))
        Dummy= ("Y-Bias: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        print (Dummy)
        time.sleep(0.5)       
        #Electron Energy
        EE=float(Controls.EEFrom.get())
        EEStr=("SetSourceOutput EE,"+str(EE)+"\r\n")
        s.send(str.encode(EEStr))
        Dummy= ("Electron Energy: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        print (Dummy)
        time.sleep(0.5)  
        #Ion Repeller
        IR=float(Controls.IRFrom.get())
        IRStr=("SetSourceOutput IR,"+str(IR)+"\r\n")
        s.send(str.encode(IRStr))
        Dummy= ("Ion Repeller: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        print (Dummy)
        time.sleep(0.5)

        #Trap Current
        s.send(b'SFCM trap\r\n')
        time.sleep(0.2)
        Dummy= ("Filament Control mode: "+s.recv(1024).decode("utf-8"))
        Controls.StatusUpdate(Dummy)
        TC=float(Controls.TCFrom.get())
        if (TC>250):
            tk.messagebox.showwarning("Warning","Trap Current limited to 250uA")
            TC=250.0
        FVStr=("SetSourceOutput TC,"+str(TC)+"\r\n")
        s.send(str.encode(FVStr))
        Dummy= ("Trap Current: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
        print (Dummy)
        Controls.StatusUpdate(Dummy)
        time.sleep(0.5)

##        
##        #Trap Voltage
##        TV=float(Controls.TVFrom.get())
##        TVStr=("SetSourceOutput TV,"+str(TV)+"\r\n")
##        s.send(str.encode(TVStr))
##        Dummy= ("Trap Voltage: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
##        print (Dummy)
##        time.sleep(0.5)
##        #Trap Voltage
##        FV=float(Controls.FVFrom.get())
##        if (FV>1.5):
##            tk.messagebox.showwarning("Warning","Filament Voltage limited to 1.5V")
##            FV=1.5
##        FVStr=("SetSourceOutput FV,"+str(FV)+"\r\n")
##        s.send(str.encode(FVStr))
##        Dummy= ("Filament Voltage: ",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
##        print (Dummy)
##        time.sleep(0.5)

        Controls.StatusUpdate("Commands Sent")

        s.close()

    def AddPTS():
        #Get Number Lines in ComboBox
        PTS=(Controls.PTSInput.get())
        print (len(PTSItem))
        PTSItem.append(PTS)
        NumItems=len(PTSItem)
        Controls.PTSList.config(values=PTSItem)

    def ClearPTS():
        #Get Number Lines in ComboBox
        PTSItem.clear()
        Controls.PTSList.config(values=PTSItem)        

    def FilOn():
        print ('Filament On')
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)

        try:
            #Connect to instrument

            s.connect(('localhost',1090))
            print (s.recv(1024).decode("utf-8"))

        except socket.error as e:
            print ("Error: ",e)
            Controls.StatusUpdate("Offline")
            return None
            
        #Login
        Controls.StatusUpdate("Logging In")
        s.send(b'login i,pw \r\n')
        time.sleep(0.2)
        print (s.recv(1024).decode("utf-8"))
        time.sleep(0.2)
        s.send(b'ver\r\n')
        time.sleep(0.2)
        print ("Version"+s.recv(1024).decode("utf-8"))
        
        s.send(b'SFCM trap\r\n')
        time.sleep(0.2)
        print ("Filament Control mode: "+s.recv(1024).decode("utf-8"))

        s.send(b'SSO TC,50\r\n')
        time.sleep(0.2)
        print ("Trap Current Set: "+s.recv(1024).decode("utf-8"))
        
        s.send(b'GFCM \r\n')
        time.sleep(0.2)
        GFCM=s.recv(1024).decode("utf-8")
        time.sleep(0.2)

        print (GFCM)        


        
        s.close()

    def FilOff():
        print ('Filament Off')
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)

        try:
            #Connect to instrument

            s.connect(('localhost',1090))
            print (s.recv(1024).decode("utf-8"))

        except socket.error as e:
            print ("Error: ",e)
            Controls.StatusUpdate("Offline")
            return None
            
        #Login
        Controls.StatusUpdate("Logging In")
        s.send(b'login i,pw \r\n')
        time.sleep(0.2)
        print (s.recv(1024).decode("utf-8"))
        time.sleep(0.2)
        s.send(b'ver\r\n')
        time.sleep(0.2)
        print ("Version"+s.recv(1024).decode("utf-8"))
        
        s.send(b'SFCM filament\r\n')
        time.sleep(0.2)
        print ("Filament Control mode: "+s.recv(1024).decode("utf-8"))

        s.send(b'SSO FV,0\r\n')
        time.sleep(0.2)
        print ("Filament Off: "+s.recv(1024).decode("utf-8"))
        
        s.send(b'GFCM \r\n')
        time.sleep(0.2)
        GFCM=s.recv(1024).decode("utf-8")
        time.sleep(0.2)

        print (GFCM)        
      
        s.close()


    #FRAME FOR PEAKS TO SCAN
    Peaksframe=tk.Frame(frame2)
    Peakslbl = tk.Label(Peaksframe, text="Peaks to Scan",width=20)
    Peakslbl.pack(side=tk.LEFT)
    Peaksframe.pack(side=tk.TOP, fill=tk.NONE)
    PTSFrame=tk.Frame(frame2)
    PTSInput = tk.Entry(PTSFrame,width=8)
    PTSInput.pack(side="left",padx=5)
    PTSAdd = tk.Button(PTSFrame, text="Add", width=4, command=AddPTS)
    PTSAdd.pack(side=tk.LEFT,padx=5)
    PTSList = ttk.Combobox(PTSFrame, values=PTSItem, width=8)
    PTSList.pack(side=tk.LEFT,padx=5)
    PTSClear = tk.Button(PTSFrame, text="Clear", width=4, command=ClearPTS)
    PTSClear.pack(side=tk.LEFT)

    PTSFrame.pack(side=tk.TOP, fill=tk.NONE)


    #FRAME FOR SETTINGS (ION ENERGY ETC)
    Settingsframe=tk.Frame(frame2)
    Settingslbl = tk.Label(Settingsframe, text="Settings",width=20)
    Settingslbl.pack(side=tk.LEFT)
    Settingsframe.pack(side=tk.TOP, fill=tk.NONE) 
    TopRow=tk.Frame(frame2)
    lblLbl = tk.Label(TopRow, text="  ",width=5,anchor='w')
    lblLbl.pack(side=tk.LEFT)
    lblSet = tk.Button(TopRow, text="Set", width=7, command=SetMassSpec)
    lblSet.pack(side=tk.LEFT)
    lblRead = tk.Button(TopRow, text="Read", width=7, command=ReadMassSpec)
    lblRead.pack(side=tk.LEFT)
    TopRow.pack(side=tk.TOP, fill=tk.NONE)
    #Ion Energy
    iEFrame=tk.Frame(frame2)
    iElbl = tk.Label(iEFrame, text="IE",width=5,anchor='w')
    iElbl.pack(side=tk.LEFT)
    iEFrom = tk.Entry(iEFrame,width=8)
    iEFrom.pack(side="left",padx=5)
    iERead = tk.Entry(iEFrame,width=8)
    iERead.pack(side="left",padx=5)
    iEFrame.pack(side=tk.TOP, fill=tk.NONE)
    #YFocus
    YFframe=tk.Frame(frame2)
    yFlbl = tk.Label(YFframe, text="YF",width=5,anchor='w')
    yFlbl.pack(side=tk.LEFT)
    yFFrom = tk.Entry(YFframe,width=8)
    yFFrom.pack(side="left",padx=5)
    yFRead = tk.Entry(YFframe,width=8)
    yFRead.pack(side="left",padx=5)
    YFframe.pack(side=tk.TOP, fill=tk.NONE)
    #YBias
    YBframe=tk.Frame(frame2)
    yBlbl = tk.Label(YBframe, text="YB",width=5,anchor='w')
    yBlbl.pack(side=tk.LEFT)
    yBFrom = tk.Entry(YBframe,width=8)
    yBFrom.pack(side="left",padx=5)
    yBRead = tk.Entry(YBframe,width=8)
    yBRead.pack(side="left",padx=5)
    YBframe.pack(side=tk.TOP, fill=tk.NONE)
    #Electron Energy
    EEframe=tk.Frame(frame2)
    EElbl = tk.Label(EEframe, text="EE",width=5,anchor='w')
    EElbl.pack(side=tk.LEFT)
    EEFrom = tk.Entry(EEframe,width=8)
    EEFrom.pack(side="left",padx=5)
    EERead = tk.Entry(EEframe,width=8)
    EERead.pack(side="left",padx=5)
    EEframe.pack(side=tk.TOP, fill=tk.NONE)
    #Ion repeller
    IRframe=tk.Frame(frame2)
    IRlbl = tk.Label(IRframe, text="IR",width=5,anchor='w')
    IRlbl.pack(side=tk.LEFT)
    IRFrom = tk.Entry(IRframe,width=8)
    IRFrom.pack(side="left",padx=5)
    IRRead = tk.Entry(IRframe,width=8)
    IRRead.pack(side="left",padx=5)
    IRframe.pack(side=tk.TOP, fill=tk.NONE)
    #Trap Voltage
    TVframe=tk.Frame(frame2)
    TVlbl = tk.Label(TVframe, text="TV",width=5,anchor='w')
    TVlbl.pack(side=tk.LEFT)
    TVFrom = tk.Entry(TVframe,width=8)
    TVFrom.pack(side="left",padx=5)
    TVRead = tk.Entry(TVframe,width=8)
    TVRead.pack(side="left",padx=5)
    TVframe.pack(side=tk.TOP, fill=tk.NONE)        
    #Filament Current
    FCframe=tk.Frame(frame2)
    FClbl = tk.Label(FCframe, text="FC",width=5,anchor='w')
    FClbl.pack(side=tk.LEFT)
    FCFrom = tk.Label(FCframe, text="",width=8)
    FCFrom.pack(side="left",padx=0)
    FCRead = tk.Entry(FCframe,width=8)
    FCRead.pack(side="left",padx=5)
    FCframe.pack(side=tk.TOP, fill=tk.NONE)     
    #Filament Voltage
    FVframe=tk.Frame(frame2)
    FVlbl = tk.Label(FVframe, text="FV",width=5,anchor='w')
    FVlbl.pack(side=tk.LEFT)
    FVFrom = tk.Label(FVframe, text="",width=8)
    FVFrom.pack(side="left",padx=0)
    FVRead = tk.Entry(FVframe,width=8)
    FVRead.pack(side="left",padx=5)
    FVframe.pack(side=tk.TOP, fill=tk.NONE)    
    #Trap Current
    TCframe=tk.Frame(frame2)
    TClbl = tk.Label(TCframe, text="TC",width=5,anchor='w')
    TClbl.pack(side=tk.LEFT)
    TCFrom = tk.Entry(TCframe,width=8)
    TCFrom.pack(side="left",padx=5)
    TCRead = tk.Entry(TCframe,width=8)
    TCRead.pack(side="left",padx=5)
    TCframe.pack(side=tk.TOP, fill=tk.NONE)    

    #Emission Current
    ECframe=tk.Frame(frame2)
    EClbl = tk.Label(ECframe, text="EC",width=5,anchor='w')
    EClbl.pack(side=tk.LEFT)
    ECFrom = tk.Label(ECframe, text="",width=8)
    ECFrom.pack(side="left",padx=0)
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
    CtrlFrame4= tk.Frame(frame2) 

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

    StatusLbl = tk.Label(frame3, text="Status",width=400)
    StatusLbl.pack(side=tk.LEFT)    

    b = tk.Button(CtrlFrame3, text="TEST", command=TestDef)
    b.pack()
    
    FilOn = tk.Button(CtrlFrame4, text="F.On", command=FilOn)
    FilOn.pack(side="left")
    FilOff = tk.Button(CtrlFrame4, text="F.Off", command=FilOff)
    FilOff.pack(side="left")

    CtrlFrame1.pack(side=tk.TOP, fill=tk.NONE,pady=3)
    CtrlFrame2.pack(side=tk.TOP, fill=tk.NONE,pady=3)
    CtrlFrame3.pack(side=tk.TOP, fill=tk.NONE,pady=5)
    CtrlFrame4.pack(side=tk.TOP, fill=tk.NONE,pady=3)    
        
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
