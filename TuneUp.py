import time
import socket

iE_=[]
Ax_=[]


print ("Peak Tune Up")

StartIE=1300
EndIE=1500

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

IE=StartIE
SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
s.send(str.encode(SVStr))
time.sleep(0.1)
IEreturn=(s.recv(1024))
time.sleep(2)

## Loop through IR, YB,YF and then scan




while (IE<(EndIE+1)):
    
    SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
    s.send(str.encode(SVStr))
    time.sleep(0.1)
    IEreturn=(s.recv(1024))
    time.sleep(0.1)

    #Acquire Data - wait for enough time for the buffer to fill....
    
    s.send(b'StartAcq 1,JS\r\n')
    time.sleep((acqRestTime))
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

    print(float(spectrum[13]))

#Calculate the peak centre
#Need iE and Ax for this.

MaxSignal = (max(Ax))
MinSignal = (min(Ax))

HalfPeakHeight=(MaxSignal-MinSignal)/2

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
    
print("Left ",FWHM_Left)
print("Right ",FWHM_Right)

PeakCentre=((FWHM_Right-FWHM_Left)/2)+FWHM_Left

print ("Centre ",PeakCentre)

#Get Hi and Low
intCentre = int(PeakCentre)

Lo = intCentre-15
Hi = intCentre+15

#Search iE to get the index of Hi and Lo

iLo = iE.index(Lo)
iHi = iE.index(Hi)
iCr =iE.index(intCentre)

LowSig=Ax[iLo]
HighSig=Ax[iHi]
CentSig=Ax[iCr]

Roundness = (CentSig - ((HighSig+LowSig)/2))/CentSig

PSF = 1/Roundness

print ("HighSig ",HighSig)
print ("Roundness ",Roundness)
print ("PSF ",PSF)

#Output to file


#Reset Arrays
iE.clear()
Ax.clear()



s.close()
