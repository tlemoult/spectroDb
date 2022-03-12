import sys,time,logging
import PyIndi
from astropy.io import fits

class TelescopeClient(PyIndi.BaseClient):
    deviceName=""
    device = None
    config = None
    
    def __init__(self,config):
        super(TelescopeClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')        
        self.logger.info('creating an instance of TelescopeClient')
        self.deviceName=config["name"]
        self.config=config
        confServer=config["server"]
        host=confServer["host"]
        port=confServer["port"]
        self.logger.info(f"set Indi server {host}:{port}")
        self.setServer(host,port)
        
    def newDevice(self, d):
        self.logger.info(f"new device {d.getDeviceName()}")
        if d.getDeviceName() == self.deviceName:
            self.logger.info(f"Found target device = {self.deviceName}")
            self.device = d
            
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        self.logger.info(f"new Text {tvp.name} for device {tvp.device}")
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        self.logger.info(f"new Message {d.messageQueue(m)}")        
    def serverConnected(self):
        self.logger.info(f"Server connected {self.getHost()}:{self.getPort()}")
    def serverDisconnected(self, code):
        self.logger.info(f"Server disconnected (exit code = {code} , {self.getHost()}:{self.getPort()}")
        
    def connect(self):
        
        self.logger.info(f"Connect to indiserver")
        if not self.connectServer():
            self.logger.error(f"Fail to connect to indi Server config={self.config}")
            self.logger.error(f"Try to run: \n  indiserver indi_simulator_telescope")
            return False
        
        self.logger.info(f"Wait device name = {self.deviceName}")
        maxAttempt = 10
        for i in range(1,maxAttempt+1):
            if self.device:
                self.logger.info(f"Found device name = {self.deviceName}")
                break
            time.sleep(0.5)
        if i == maxAttempt:
            self.logger.error("Fail to found device name ")
            return False

        self.logger.info("wait CONNECTION property be defined for telescope")        
        maxAttempt = 10
        for i in range(1,maxAttempt+1):
            if self.device.getSwitch("CONNECTION"):
                self.logger.info("Found swich CONNECTION")
                break
            time.sleep(0.5)

        if i == maxAttempt:
            self.logger.error("Fail to connect find CONNECTION switch")
            return False

    
        # if the telescope device is not connected, we do connect it
        if not(self.device.isConnected()):
            self.logger.info("Connect to telescope Now, send the switch")
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            telescope_connect = self.device.getSwitch("CONNECTION")
            telescope_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            telescope_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            self.sendNewSwitch(telescope_connect) # send this new value to the device

        self.logger.info("Telecope is connected")

        return True
    
    def getCoordinates(self):
        telescope_radec=self.device.getNumber("EQUATORIAL_EOD_COORD")
        while not(telescope_radec):
            time.sleep(0.5)
            telescope_radec=self.device.getNumber("EQUATORIAL_EOD_COORD")

        ra = telescope_radec[0].value
        dec = telescope_radec[1].value
        self.logger.info(f"get telescope coordinates  ra={ra}   dec = {dec}")
        return {'ra':ra,'dec':dec,'EPOCH':'JNow','Unit':'ra:Hours dec:Degrees'}             

    def setCoordinates(self,coords):
        telescope_radec=self.device.getNumber("EQUATORIAL_EOD_COORD")
        while not(telescope_radec):
            time.sleep(0.5)
            telescope_radec=self.device.getNumber("EQUATORIAL_EOD_COORD")

        telescope_radec[0].value = coords['ra']
        telescope_radec[1].value = coords['dec']
        self.sendNewNumber(telescope_radec)
        self.logger.info(f"set telescope coordinates  coords={coords}")
        
        