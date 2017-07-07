import sys,time, logging,json
import PyIndi


class IndiClient(PyIndi.BaseClient):
    deviceName=""
    device = None
    filePath= "."
    fileNameRoot= "OBJECT-"
    currentIndex= 1
    expTime=1
    serieRun=False
    setPointTemperature=0
    ccdTemperature=+32000

    def __init__(self,deviceName):
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')        
        self.logger.info('creating an instance of PyQtIndi.IndiClient')
        self.deviceName=deviceName

    def newAcquSerie(self,filePath,fileNameRoot,nbExposure,expTime):
        self.logger.info("<<<<<<< New acquisition serie fileName=%s nbExposure=%d, expTime=%d"%(fileNameRoot,nbExposure,expTime))
        self.currentIndex= 1
        self.filePath=filePath
        self.fileNameRoot=fileNameRoot
        self.nbExposure=nbExposure
        self.expTime=expTime
        self.serieRun=True
        self.takeExposure(expTime)

    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName())
        if d.getDeviceName() == self.deviceName:
            self.logger.info("Found target device =%s"%self.deviceName)
            # save reference to the device in member variable
            self.device = d

    def newProperty(self, p):
        self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
        if self.device is not None and p.getName() == "CONNECTION" and p.getDeviceName() == self.device.getDeviceName():
            self.logger.info("Got property CONNECTION for CCD Simulator!")
            # connect to device
            self.connectDevice(self.device.getDeviceName())
            # set BLOB mode to BLOB_ALSO
            self.setBLOBMode(1, self.device.getDeviceName(), None)
        if p.getName() == "CCD_EXPOSURE":
            self.logger.info("Got CCD_Exposure Property")
            pass

        if p.getName() == "CCD_TEMPERATURE":
            self.logger.info("Got temperature Property")

    def removeProperty(self, p):
        self.logger.info("remove property "+ p.getName() + " for device "+ p.getDeviceName())

    def newBLOB(self, bp):
        self.logger.info("new BLOB "+ bp.name.decode())
        # get image data
        img = bp.getblobdata()
        import cStringIO
        # write image data to StringIO buffer
        blobfile = cStringIO.StringIO(img)
        # open a file and save buffer to disk
        fullPath=self.filePath+'/'+self.fileNameRoot+str(self.currentIndex)+".fits"
        self.logger.info("save file to "+fullPath)
        with open(fullPath, "wb") as f:
            f.write(blobfile.getvalue())
        # start new exposure for acqusition serie 
        self.currentIndex+=1
        if (self.currentIndex<=self.nbExposure):
            self.takeExposure(self.expTime)
            self.serieRun=True
        else:
            self.serieRun=False
        
    def newSwitch(self, svp):
        self.logger.info ("new Switch "+ svp.name.decode()  +" for device "+ svp.device.decode())
    def newNumber(self, nvp):
        self.logger.info("new Number "+ nvp.name.decode() + " value= %.2f"%(nvp[0].value)+ " for device "+ nvp.device.decode())
        if nvp.name.decode()=="CCD_TEMPERATURE":
            self.ccdTemperature=nvp[0].value

        if nvp.name.decode()=="CCD_EXPOSURE":
            self.ccdExposure=nvp[0].value

    def newText(self, tvp):
        self.logger.info("new Text "+ tvp.name.decode() + " for device "+ tvp.device.decode())
    def newLight(self, lvp):
        self.logger.info("new Light "+ lvp.name.decode() + " for device "+ lvp.device.decode())
    def newMessage(self, d, m):
        self.logger.info("new Message "+ d.messageQueue(m).decode())
    def serverConnected(self):
        print("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")


    def takeExposure(self,expTime):
        self.logger.info("<<<<<<<< Take Exposure, duration=%.2f >>>>>>>>>"%(expTime))
        #get current exposure time
        exp = self.device.getNumber("CCD_EXPOSURE")
        # set exposure time to 5 seconds
        exp[0].value = expTime
        # send new exposure time to server/device
        self.sendNewNumber(exp)
        self.ccdExposure=expTime

    def setTemperature(self,setPointTemperature):
        self.setPointTemperature=setPointTemperature
        self.logger.info("<<<<<<<<< Set Temperature set point =%.2f >>>>>>>>"%setPointTemperature)
        t=self.device.getNumber("CCD_TEMPERATURE")
        t[0].value = setPointTemperature
        self.sendNewNumber(t)

    def isCCDTemperatureOK(self):
        e=self.ccdTemperature-self.setPointTemperature
        self.logger.info("ccdTemp=%.1f  setPoint=%.1f  err=%.1f"%(self.ccdTemperature,self.setPointTemperature,e))
        return abs(e)<2.0

    def setBinning(self,binning):
        self.binning=binning
        self.logger.info("<<<<<<< Set binning to X=%d Y=%d"%(binning['X'],binning['Y']))
        b=self.device.getNumber("CCD_BINNING")
        b[0].value=binning['X']
        b[1].value=binning['Y']
        self.sendNewNumber(b)

def waitEndAcqSerie(indiclient):
    while indiclient.serieRun==True:
        print """Exposure: %d/%d "%s" %.1f/%.1f seconds."""%( indiclient.currentIndex, indiclient.nbExposure  ,indiclient.fileNameRoot,indiclient.expTime-indiclient.ccdExposure,indiclient.expTime)
        time.sleep(1)

#load configuration
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
print config
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
# instantiate the client, for camera
indiclient=IndiClient(config['ccdSpectro']['name'])
# set indi server
server=config['ccdSpectro']['server']
indiclient.setServer(str(server['host']),server['port'])
# connect to indi server
print("Connecting and waiting 2secs")
if (not(indiclient.connectServer())):
     print("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort())+" - Try to run")
     print("  indiserver indi_simulator_ccd")
     sys.exit(1)
time.sleep(1)

#set binning
indiclient.setBinning(config['ccdSpectro']['binning'])
#set temperature of CCD
print("setTemperature")
indiclient.setTemperature(config['ccdSpectro']['tempSetPoint'])
while not indiclient.isCCDTemperatureOK():
    print "   CCD temperature=%.1f"%indiclient.ccdTemperature
    time.sleep(2)

#acquisition
print "run acquisition" 
indiclient.newAcquSerie(config['path']['acquire'],"OBJECT-",4,10)
waitEndAcqSerie(indiclient)

print "run acquisition" 
indiclient.newAcquSerie(config['path']['acquire'],"FLAT-",4,1)
waitEndAcqSerie(indiclient)

print("acquisition finished")
