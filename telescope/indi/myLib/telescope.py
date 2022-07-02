import sys,time,logging
import PyIndi
from astropy.io import fits
from astropy.coordinates import SkyCoord,FK5,AltAz,EarthLocation
import astropy.units as u
from astropy.time import Time

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
        self.logger.info(f"get telescope coordinates EPOCHJNow ra={ra} Hours   dec = {dec}")
        c = SkyCoord(ra,dec,unit=(u.hourangle, u.deg),frame='icrs', equinox=Time.now())
        return c

    def setCoordinates(self,coords):
        propertyNameCoord="EQUATORIAL_EOD_COORD"
        telescope_radec=self.device.getNumber(propertyNameCoord)
        while not(telescope_radec):
            time.sleep(0.5)
            telescope_radec=self.device.getNumber(propertyNameCoord)

        ra=coords.ra.value/360*24
        dec=coords.dec.value
        print(f"setCoordinates with property={propertyNameCoord} ra={coords.ra.value} dec={coords.dec.value}")
        
        telescope_radec[0].value = ra
        telescope_radec[1].value = dec
        self.sendNewNumber(telescope_radec)
        self.logger.info(f"set telescope coordinates  coords={coords}\n ra_hms={coords.ra.hms}   dec_dms = {coords.dec.dms} \n ra_value={coords.ra.value} dec_value={coords.dec.value}")
        while (telescope_radec.s==PyIndi.IPS_BUSY):
            print(f"Scope Moving to RA={coords.ra.value}  DEC= {coords.dec.value}")
            time.sleep(1)
            
    
    def onCoordSet(self,action):
        telescope_on_coord_set=self.device.getSwitch("ON_COORD_SET")
        while not(telescope_on_coord_set):
            time.sleep(0.5)
            telescope_on_coord_set=self.device.getSwitch("ON_COORD_SET")
        
        if action == 'TRACK':
            self.logger.info(f"set telescope action onCoordSet {action}")
            telescope_on_coord_set[0].s=PyIndi.ISS_ON
            telescope_on_coord_set[1].s=PyIndi.ISS_OFF
            telescope_on_coord_set[2].s=PyIndi.ISS_OFF
        elif action == 'SLEW':
            self.logger.info(f"set telescope action onCoordSet {action}")
            telescope_on_coord_set[0].s=PyIndi.ISS_OFF
            telescope_on_coord_set[1].s=PyIndi.ISS_ON
            telescope_on_coord_set[2].s=PyIndi.ISS_OFF
        elif action == 'SYNC':
            self.logger.info(f"set telescope action onCoordSet {action}")
            telescope_on_coord_set[0].s=PyIndi.ISS_OFF
            telescope_on_coord_set[1].s=PyIndi.ISS_OFF
            telescope_on_coord_set[2].s=PyIndi.ISS_ON
        else:
            self.logger.info(f"set telescope action onCoordSet Undefined")
        self.sendNewSwitch(telescope_on_coord_set)
