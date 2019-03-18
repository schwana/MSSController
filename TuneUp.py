import time
import socket
import os
from datetime import datetime


def outputData(iE,Ax,DataString):
    os.chdir("c:\\MSSData")
    file_to_open = "TuneNum.txt"
    #Get current tune run number
    fo = open(file_to_open, "r")
    TuneNum = fo.readline()
    fo.close()
    FileName = 'Tune'+TuneNum+'.csv'
    foInitial = open(FileName,"a")
    foInitial.write("iE,Ax"+"\n")
    foInitial.close()

    foRun = open(FileName,"a")
    #Collected data
    for x in range (0, len(iE)):
        outputString=(str(iE[x])+","+str(Ax[x]))
        foRun.write(outputString+'\n')
    foRun.close()
    
    foUpdate = open("TuneNum.txt", "w")
    S=int(float(TuneNum))
    S=S+1
    foUpdate = open("TuneNum.txt", "w")
    foUpdate.write(str(S))
    foUpdate.close()
    #append dataline to summary file
    foSummary = open("Summary.csv","a")
    foSummary.write('\n'+str((TuneNum))+","+DataString)
    foSummary.close()

def Standard():
    #Do a standard settings run
    print("Running Standard")
    YF=70
    YB=1.4
    IR=6.1
    
    YFStr=("SetSourceOutput YF, 70 \r\n")
    s.send(str.encode(YFStr))
    time.sleep(0.1)
    YFreturn=(s.recv(1024))
    time.sleep(1)

    YBStr=("SetSourceOutput YB, 1.4 \r\n")
    s.send(str.encode(YBStr))
    time.sleep(0.1)
    YBreturn=(s.recv(1024))
    time.sleep(1)

    IRStr=("SetSourceOutput IR, 6.1 \r\n")
    s.send(str.encode(IRStr))
    time.sleep(0.1)
    IRreturn=(s.recv(1024))
    time.sleep(1)
            
    IE=StartIE
    SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
    s.send(str.encode(SVStr))
    time.sleep(0.1)
    IEreturn=(s.recv(1024))
    time.sleep(2)

    while (IE<(EndIE+1)):
        
        SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
        s.send(str.encode(SVStr))
        time.sleep(0.1)
        IEreturn=(s.recv(1024))
        time.sleep(0.1)

        #Acquire Data - wait for enough time for the buffer to fill....
        
        s.send(b'StartAcq 1,JS\r\n')
        time.sleep((0.3))
        returnString=s.recv(1024)
        time.sleep(0.1)
       #Separate the string
        spec=(returnString.decode("utf-8"))
        rS=(str(IE)+","+spec)
        rS=rS[0:-5]
        spectrum=rS.split(',')

        #print (spectrum)
        #Add the inidividual readings to the relevent array
        #for data output and plotting
        
        iE_.append(float(spectrum[0]))
        Ax_.append(float(spectrum[13]))

        iE=iE_
        Ax=Ax_
        N=len(iE)
       
        IE=IE+1

       # print(float(spectrum[13]))

    #Calculate the peak centre
    #Need iE and Ax for this.

    MaxSignal = (max(Ax))
    MinSignal = (min(Ax))

    HalfPeakHeight=(MaxSignal-MinSignal)/2

    PeakCentre=0

    if (HalfPeakHeight>0.05):
        #Loop beween Start IE and midIE to look for voltage
        #where Ax is HalfPeakheight
        TestVoltage=StartIE
        i=0
        while (TestVoltage<EndIE):

            if (Ax[i]>HalfPeakHeight):
                FWHM_Left=iE[i]
                break
            i=i+1
            TestVoltage=TestVoltage+1

        TestVoltage=StartIE
        i=0
        while (TestVoltage<EndIE):

            if(TestVoltage>(FWHM_Left+20)):

                if (Ax[i]<HalfPeakHeight):
                    FWHM_Right=iE[i]
                    break
            i=i+1
            TestVoltage=TestVoltage+1
            


        PeakCentre=((FWHM_Right-FWHM_Left)/2)+FWHM_Left



        #Get Hi and Low
        intCentre = int(PeakCentre)

        Lo = intCentre-Shoulders
        Hi = intCentre+Shoulders

        #Search iE to get the index of Hi and Lo

        iLo = iE.index(Lo)
        iHi = iE.index(Hi)
        iCr = iE.index(intCentre)

        LowSig=Ax[iLo]
        HighSig=Ax[iHi]
        CentSig=Ax[iCr]

        Roundness = (CentSig - ((HighSig+LowSig)/2))/CentSig

        PSF = 1/Roundness
    else:
        HighSig=0
        Roundness=0
        PSF=0

    CurTime=str(datetime.now())

    #Output to file
    #Open and append summary
    print ("Filename ",CurTime,YF,YB,IR,HighSig,PSF,PeakCentre)
    DataString=(CurTime+","+str(YF)+","+str(YB)+","+str(IR)+","+str(HighSig)+","+str(PSF)+","+str(PeakCentre))
    #Create and save scan
    outputData(iE,Ax,DataString)
    #Reset Arrays
    iE.clear()
    Ax.clear()


iE_=[]
Ax_=[]


print ("Peak Tune Up")

StartIE=1300
EndIE=1500

StartIR=-5
EndIR=15

StartYB=-15
EndYB=20

StartYF=60
EndYF=64

Shoulders=10

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

acqAStr=("SetAcqPeriod 100 \r\n")
s.send(str.encode(acqAStr))
time.sleep(0.2)
Dummy= ("SetAcqPeriod",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
acqRestTime=0.2



## Loop through IR, YB,YF and then scan

YF=StartYF
while (YF<(EndYF+5)):
    YFStr=("SetSourceOutput YF,"+str(YF)+"\r\n")
    s.send(str.encode(YFStr))
    time.sleep(0.1)
    YFreturn=(s.recv(1024))
    time.sleep(1)

    YB=StartYB
    while (YB<(EndYB+1)):

        Standard()

        YFStr=("SetSourceOutput YF,"+str(YF)+"\r\n")
        s.send(str.encode(YFStr))
        time.sleep(0.1)
        YFreturn=(s.recv(1024))
        time.sleep(1)

        YBStr=("SetSourceOutput YB,"+str(YB)+"\r\n")
        s.send(str.encode(YBStr))
        time.sleep(0.1)
        YBreturn=(s.recv(1024))
        time.sleep(1)

        

        IR=StartIR
        while (IR<(EndIR+1)):

            
            IRStr=("SetSourceOutput IR,"+str(IR)+"\r\n")
            s.send(str.encode(IRStr))
            time.sleep(0.1)
            IRreturn=(s.recv(1024))
            time.sleep(1)

            IE=StartIE
            SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
            s.send(str.encode(SVStr))
            time.sleep(0.1)
            IEreturn=(s.recv(1024))
            time.sleep(2)

            while (IE<(EndIE+1)):
                
                SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
                s.send(str.encode(SVStr))
                time.sleep(0.1)
                IEreturn=(s.recv(1024))
                time.sleep(0.1)

                #Acquire Data - wait for enough time for the buffer to fill....
                
                s.send(b'StartAcq 1,JS\r\n')
                time.sleep((0.3))
                returnString=s.recv(1024)
                time.sleep(0.1)
               #Separate the string
                spec=(returnString.decode("utf-8"))
                rS=(str(IE)+","+spec)
                rS=rS[0:-5]
                spectrum=rS.split(',')

                #print (spectrum)
                #Add the inidividual readings to the relevent array
                #for data output and plotting
                
                iE_.append(float(spectrum[0]))
                Ax_.append(float(spectrum[13]))

                iE=iE_
                Ax=Ax_
                N=len(iE)
               
                IE=IE+1

                

            #Calculate the peak centre
            #Need iE and Ax for this.

            MaxSignal = (max(Ax))
            MinSignal = (min(Ax))

            HalfPeakHeight=(MaxSignal-MinSignal)/2

            PeakCentre=0

            if (HalfPeakHeight>0.05):
                #Loop beween Start IE and midIE to look for voltage
                #where Ax is HalfPeakheight
                TestVoltage=StartIE
                i=0
                while (TestVoltage<EndIE):

                    if (Ax[i]>HalfPeakHeight):
                        FWHM_Left=iE[i]
                        break
                    i=i+1
                    TestVoltage=TestVoltage+1

                TestVoltage=StartIE
                i=0
                while (TestVoltage<EndIE):

                    if(TestVoltage>(FWHM_Left+20)):

                        if (Ax[i]<HalfPeakHeight):
                            FWHM_Right=iE[i]
                            break
                    i=i+1
                    TestVoltage=TestVoltage+1
                    


                PeakCentre=((FWHM_Right-FWHM_Left)/2)+FWHM_Left



                #Get Hi and Low
                intCentre = int(PeakCentre)

                Lo = intCentre-Shoulders
                Hi = intCentre+Shoulders

                #Search iE to get the index of Hi and Lo

                iLo = iE.index(Lo)
                iHi = iE.index(Hi)
                iCr = iE.index(intCentre)

                LowSig=Ax[iLo]
                HighSig=Ax[iHi]
                CentSig=Ax[iCr]

                Roundness = (CentSig - ((HighSig+LowSig)/2))/CentSig

                PSF = 1/Roundness
            else:
                HighSig=0
                Roundness=0
                PSF=0

            CurTime=str(datetime.now())

            #Output to file
            #Open and append summary
            print ("Filename ",CurTime,YF,YB,IR,HighSig,PSF,PeakCentre)
            DataString=(CurTime+","+str(YF)+","+str(YB)+","+str(IR)+","+str(HighSig)+","+str(PSF)+","+str(PeakCentre))
            #Create and save scan
            outputData(iE,Ax,DataString)
            #Reset Arrays
            iE.clear()
            Ax.clear()

            IR=IR+1

        YB=YB+1
        
    YF=YF+5

Standard()


s.close()
