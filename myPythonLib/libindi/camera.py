import sys,time,logging
import PyIndi
from astropy.io import fits

from libcalc.img import statSpectrum
import matplotlib.pyplot as plt

class CameraClient(PyIndi.BaseClient):
    deviceName=""
    device = None
    filePath= "."
    fileNameRoot= "OBJECT-"
    currentIndex= 1
    expTime=1
    serieRun=False
    setPointTemperature=0
    ccdTemperature=+32000


    def __init__(self,cameraConf):
        super(CameraClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')        
        self.logger.info(f'creating an instance of CameraClient with cameraConf={cameraConf}')
        self.deviceName=cameraConf["name"]
        self.setServer(cameraConf["server"]["host"],cameraConf["server"]["port"])

        if (not(self.connectServer())):
            self.logger.error(f"Fail to connect to indi Server {self.getHost()}:{self.getPort()}")
            self.logger.error("Try to run:")
            self.logger.error("  indiserver indi_simulator_ccd")
            raise NameError(f'Fail to connect to indi Server {self.getHost()}:{self.getPort()}')

        self.logger.info("connecting to camera")
        if (not(self.waitCameraConnected())):
            self.logger.error(f"Fail to connect to camera {self.deviceName}")
            self.disconnectServer()
            raise NameError(f'Fail to connect to camera {self.deviceName}')

        self.logger.info("set binnig")
        self.setBinning({'X':cameraConf["binning"]["X"],'Y':cameraConf["binning"]["Y"]})

        if "tempSetPoint" in cameraConf.keys():
            self.logger.info("set CCD temperature")
            self.setTemperature(cameraConf['tempSetPoint'])
            self.waitCCDTemperatureOK()
        else:
            self.logger.info("No temperature set")


#    def __init__(self,deviceName,host,port):
#        super(CameraClient, self).__init__()
#        self.logger = logging.getLogger('PyQtIndi.IndiClient')        
#        self.logger.info('creating an instance of IndiClient')
#        self.deviceName=deviceName
#        self.setServer(host,port)

    def newAcquSerie(self,filePath,fileNameRoot,nbExposure,expTime,display_spectrum=False):
        self.logger.info("<<<<<<< New acquisition serie fileName=%s nbExposure=%d, expTime=%d"%(fileNameRoot,nbExposure,expTime))
        self.currentIndex= 1
        self.filePath=filePath
        self.fileNameRoot=fileNameRoot
        self.nbExposure=nbExposure
        self.expTime=expTime
        self.serieRun=True
        self.takeExposure(expTime)
        self.display_spectrum = display_spectrum
        self.last_image_filepath = ''
        self.is_a_image_to_display = False

    def newDevice(self, d):
        self.logger.info(f"new device {d.getDeviceName()}")
        if d.getDeviceName() == self.deviceName:
            self.logger.info(f"Found target device = {self.deviceName}")
            # save reference to the device in member variable
            self.device = d

    def newProperty(self, p):
        #self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
        if p.getName() == "CONNECTION" and p.getDeviceName() == self.deviceName:
            self.logger.info("Got property CONNECTION for "+ p.getDeviceName())
            self.connectDevice(self.device.getDeviceName())
            self.setBLOBMode(1, self.device.getDeviceName(), None)
            self.logger.info(f"Connected to {p.getDeviceName()}")

        if p.getName() in { "CCD_EXPOSURE", "CCD_TEMPERATURE"}:
            self.logger.info(f"Got Property {p.getName} = {p.getNumber}")

    def removeProperty(self, p):
        self.logger.info(f"remove property {p.getName()} for device {p.getDeviceName()}")

    def updateProperty(self, prop):
        if prop.getType() == PyIndi.INDI_NUMBER:
            self.newNumber(PyIndi.PropertyNumber(prop))
        elif prop.getType() == PyIndi.INDI_SWITCH:
            self.newSwitch(PyIndi.PropertySwitch(prop))
        elif prop.getType() == PyIndi.INDI_TEXT:
            self.newText(PyIndi.PropertyText(prop))
        elif prop.getType() == PyIndi.INDI_LIGHT:
            self.newLight(PyIndi.PropertyLight(prop))
        elif prop.getType() == PyIndi.INDI_BLOB:
            self.newBLOB(PyIndi.PropertyBlob(prop)[0])

    def newBLOB(self, bp):

        #self.logger.debug(f"new BLOB name = {bp.name}   device = {bp.bvp.device}")
        
        if self.device==None:
            return

        if bp.bvp.device == self.device.getDeviceName():
            # get image data
            self.logger.info(f"get BLOB from our camera {bp.bvp.device}")
            
            fullPath=self.filePath+'/'+self.fileNameRoot+str(self.currentIndex)+".fits"
            self.logger.info("save file to "+fullPath)

            data = bp.getblobdata()
            f = open(fullPath, 'wb')
            f.write(data)
            f.close()

            if self.display_spectrum:
                self.last_image_filepath = fullPath
                self.is_a_image_to_display = True
                        
            # start new exposure for acqusition serie 
            self.currentIndex+=1
            if (self.currentIndex<=self.nbExposure):
                self.takeExposure(self.expTime)
                self.serieRun=True
            else:
                self.serieRun=False
        
    def newSwitch(self, svp):
        self.logger.info (f"new Switch {svp.getName()} for device {svp.getDeviceName()}")       

    def newNumber(self, nvp):
        #self.logger.debug(f"root new Number {nvp.getName()} = {nvp[0].getValue():.2f} for device {nvp.getDeviceName()}")

        if self.device==None:
            return

        if nvp.getDeviceName() == self.device.getDeviceName():
            self.logger.info(f"new Number {nvp.getName()} = {nvp[0].getValue():.2f} for my device {nvp.getDeviceName()}")

            if nvp.getName() == "CCD_TEMPERATURE":
                self.ccdTemperature=nvp[0].getValue()

            if nvp.getName() == "CCD_EXPOSURE":
                self.ccdExposure=nvp[0].getValue()

    def newText(self, tvp):
        self.logger.info(f"new Text {tvp.getName()} for device {tvp.getDeviceName()}")
    def newLight(self, lvp):
        self.logger.info(f"new Light {lvp.getName()} for device {lvp.getDeviceName}")
    def newMessage(self, d, m):
        self.logger.info(f"new Message {d.messageQueue(m)}")
    def serverConnected(self):
        self.logger.info(f"Server connected {self.getHost()}:{self.getPort()}")
    def serverDisconnected(self, code):
        self.logger.info(f"Server disconnected (exit code = {code} , {self.getHost()}:{self.getPort()}")

    def takeExposure(self,expTime):
        self.logger.info(f"<<<<<<<< Take Exposure, duration={expTime} >>>>>>>>>")
        exp = self.device.getNumber("CCD_EXPOSURE")
        exp[0].setValue(expTime)
        # send new exposure time to server/device
        self.sendNewNumber(exp)
        self.ccdExposure=expTime

    def setObserverAndObjectName(self,obsName,objectName):
        self.logger.info(f"<<<<<<<<< setObserverAndObjectName in FITS  obsName= {obsName}  objectName= {objectName}")
        t=self.device.getText("FITS_HEADER")
        t[0].name = "FITS_OBSERVER"
        t[0].text = obsName
        t[1].name = "FITS_OBJECT"
        t[1].text = objectName
        self.sendNewText(t)

    def setTemperature(self,setPointTemperature):
        self.setPointTemperature=setPointTemperature
        self.logger.info(f"<<<<<<<<< Set Temperature set point = {setPointTemperature:.2f}")
        for tWait in range(10):
            t=self.device.getNumber("CCD_TEMPERATURE")
            if not t==None:
                self.logger.info(f"Found CCD_TEMPERATURE property")
                t[0].setValue(setPointTemperature)
                self.sendNewNumber(t)
                self.logger.info("Set temperature is OK")
                return True

            self.logger.info(f"Waiting CCD_TEMPERATURE property  ")
            time.sleep(1)
        self.logger.error(f"Time out in setTemperature")


    def isCCDTemperatureOK(self):
        e=self.ccdTemperature-self.setPointTemperature
        self.logger.info(f"is CCDTemperatureOK: ccdTemp = {self.ccdTemperature:.1f}   setPoint = {self.setPointTemperature:.1f}   err = {e:.1f}")
        return abs(e)<1.0

    def waitCCDTemperatureOK(self):
        while True:
            print(f"\r  CCD temperature = {self.ccdTemperature:.1f} / setPoint = {self.setPointTemperature}     ",end='',flush=True)
            if self.isCCDTemperatureOK():
                break
            time.sleep(1)
        print('\nTemperature setPoint reached.')

    def waitCameraConnected(self):
        for t in range(10):
            if not self.device==None:
                self.logger.info("Camera Connected")
                return True
            #print("\rWaiting camera connection  ",end='',flush=True)
            time.sleep(0.5)
        
        self.logger.info("Time out, no camera found")
        return False


    def setBinning(self,binning):
        self.binning=binning
        self.logger.info(f"<<<<<<< Set binning to X={binning['X']} Y={binning['Y']}")

        for t in range(10):
            self.logger.info(f" t= {t}")
            b=self.device.getNumber("CCD_BINNING")
            self.logger.info(f" b= {b}  type(b) = {type(b)}")
            if not b==None:
                self.logger.info(f"Found CCD_BINING_ property")
                b[0].setValue(binning['X'])
                b[1].setValue(binning['Y'])
                self.sendNewNumber(b)
                self.logger.info("Binning set OK")
                return True

            #print("\r  Waiting CCD_BINNNIG property  ",end='',flush=True)
            time.sleep(1)

        self.logger.error(f"Time out.. CCD_BINNING property not found")
        return False


    def waitEndAcqSerie(self):
        if self.display_spectrum:
            plt.ion()
            plt.show()
            fig, (ax1, ax2) = plt.subplots(2,sharex=True,figsize=(12, 7))
            fig.suptitle('preview spectrum')
            ax1.set_title("2D image")
            ax2.set_title("binned profil")
            ax2.set_xlabel("pixel X coord")

        while self.serieRun==True:
            if self.display_spectrum and self.is_a_image_to_display:
                self.is_a_image_to_display = False
                stat = statSpectrum(self.last_image_filepath,binnigHeight = 60)

                print(f"Mean = {round(stat['mean'])} Max = {stat['max']}")

                ax1.imshow(stat['img'], cmap=plt.cm.gray) 
                ax2.plot(stat['spectrum'],label=f"exposure no {self.currentIndex-1}")
                ax2.legend(loc='upper right')
                plt.draw()
                plt.pause(0.2)

            out=f"""Exposure: "{self.fileNameRoot}" {self.currentIndex}/{self.nbExposure}  {self.expTime-self.ccdExposure:.1f}/{self.expTime:.1f} seconds."""
            sys.stdout.write('\r'+out)
            sys.stdout.flush()
            time.sleep(1)
        print(" ")

        plt.close()
