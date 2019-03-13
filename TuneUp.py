import time
import socket

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

print ("Peak Centering")
PeakToScan=1390
print (PeakToScan)

StartIE=PeakToScan-40
EndIE=PeakToScan+40

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
acqTime=AqTime.get()
acqAStr=("SetAcqPeriod 100 \r\n")
s.send(str.encode(acqAStr))
time.sleep(0.2)
Dummy= ("SetAcqPeriod",s.recv(1024).decode("utf-8").replace('\n', ' ').replace('\r', ''))
acqRestTime=0.1+(acqTime/1000)

IE=StartIE
SVStr=("SetSourceOutput IE,"+str(IE)+"\r\n")
s.send(str.encode(SVStr))
time.sleep(0.1)
IEreturn=(s.recv(1024))
time.sleep(5)

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

    rS_String=(","+str(0.0) + ","+str(0.0)+ ","+str(0.0)+ "," +
                str(0.0)+ "," +
                str(0.0)+ "," +
                str(0.0)+ "," +
                str(0.0)+ "," +
                str(0.0)+ "," +
                str(0.0)+ "," +
                str(0.0)+ ",")

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
    rS=(str(IE)+","+spec2)
    rS=rS[0:-1]
    spectrum=rS.split(',')

    #print (spectrum)
    #Add the inidividual readings to the relevent array
    #for data output and plotting
    rS_.append(rS_String)
    iE_.append(float(spectrum[0]))
    L5_.append(0.0)
    L4_.append(0.0)
    L3_.append(0.0)
    L2_.append(0.0)
    L1_.append(0.0)
    Ax_.append(float(spectrum[13]))
    H1_.append(0.0)
    H2_.append(0.0)
    H3_.append(0.0)
    H4_.append(0.0)

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
   
    IE=IE+1

    print(float(spectrum[13]))
    

s.close()


#Calculate the peak centre
#Need iE and Ax for this.

print (max(Ax))
print (min(Ax))

HalfPeakHeight=(max(Ax)-min(Ax))/2

#Loop beween Start IE and midIE to look for voltage
#where Ax is HalfPeakheight
TestVoltage=StartIE
i=0
while (TestVoltage<PeakToScan):

    if (Ax[i]>HalfPeakHeight):
        FWHM_Left=iE[i]
        break
    i=i+1
    TestVoltage=TestVoltage+1

TestVoltage=StartIE
i=0
while (TestVoltage<EndIE):

    if(TestVoltage>PeakToScan):

        if (Ax[i]<HalfPeakHeight):
            FWHM_Right=iE[i]
            break
    i=i+1
    TestVoltage=TestVoltage+1
    
print(FWHM_Left)
print(FWHM_Right)

PeakCentre=((FWHM_Right-FWHM_Left)/2)+FWHM_Left

print (PeakCentre)

Offset= PeakToScan-PeakCentre

Controls.PTSOffset.delete(0,tk.END)
Controls.PTSOffset.insert(1,str(Offset)) 


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
