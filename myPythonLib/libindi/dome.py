import sys,time,logging,os,json,logging
import PyIndi
from libcalc.dome import calc_azimuth

class DomeClient(PyIndi.BaseClient):
    deviceName=""
    device = None
    config = None
    
    def __init__(self,config):
        super(DomeClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')        
        self.logger.info('creating an instance of DomeClient')
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
        self.logger.info( "new property " + p.getName() + " for device " + p.getDeviceName() )
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
    def newSwitch(self, svp):
        self.logger.info(f"newSwitch name = {svp.name} for device {svp.device}")
    def newNumber(self, nvp):
        self.logger.info(f"newNumber name = {nvp.name} for device {nvp.device}")
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
        
        self.logger.info(f"Connect to indiserver for Dome")

        if not self.isServerConnected():
            if not self.connectServer():
                self.logger.error(f"Fail to connect to indi Server config={self.config}")
                self.logger.error(f"Try to run: \n  indiserver indi_simulator_Dome")
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
            self.disconnectServer()
            return False

        self.logger.info("wait CONNECTION property be defined for Dome")        
        maxAttempt = 10
        for i in range(1,maxAttempt+1):
            if self.device.getSwitch("CONNECTION"):
                self.logger.info("Found swich CONNECTION")
                break
            time.sleep(0.5)

        if i == maxAttempt:
            self.logger.error("Fail to connect find CONNECTION switch")
            self.disconnect()
            return False

        # if the Dome device is not connected, we do connect it
        if not(self.device.isConnected()):
            self.logger.info("Connect to Dome Now, send the switch")
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            Dome_connect = self.device.getSwitch("CONNECTION")
            Dome_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            Dome_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            self.sendNewSwitch(Dome_connect) # send this new value to the device
            
        else:
            self.logger.info("Dome already connected")

        while not (self.device.isConnected()):
            time.sleep(0.2)

        self.logger.info("Dome is connected")        

    def disconnect(self):
        Dome_disconnect = self.device.getSwitch("CONNECTION")
        Dome_disconnect[0].s=PyIndi.ISS_OFF  # the "CONNECT" switch
        Dome_disconnect[1].s=PyIndi.ISS_ON # the "DISCONNECT" switch
        self.sendNewSwitch(Dome_disconnect) # send this new value to the device

        while self.device.isConnected():
            print(".",end="")
            time.sleep(0.2)

        self.logger.info("Dome is disconnected")  

        self.disconnectServer()
        while self.isServerConnected():
            print(".",end="")
            time.sleep(0.2)

        self.logger.info("Dome server is disconnected")  

        return True

    def get_shutter(self):
        self.logger.info(f"dome: get shutter status")
        
        
        #force fresh connection to get updated data..
        if self.device.isConnected():
            self.disconnect()
        self.connect()

        time.sleep(1)
        dome_shutter = self.device.getSwitch("DOME_SHUTTER")

        state = [ dome_shutter[0].s , dome_shutter[1].s]
        if state == [0,1]:
            value = "close"
        elif state == [1,0]:
            value = "open"
        
        str_log = f"dome: shutter status is {value}"
        print(str_log)
        self.logger.info(str_log)

        return value

    def set_shutter(self,order):
        print(f"dome: set shutter to ({order})")
        self.logger.info(f"dome: set shutter({order})")

        #prepare the order
        if order == "open":
            order_vector = [PyIndi.ISS_ON,PyIndi.ISS_OFF]
        elif order == "close":
            order_vector = [PyIndi.ISS_OFF,PyIndi.ISS_ON]
        else:
            return False

        # send the order
        dome_shutter = self.device.getSwitch("DOME_SHUTTER")
        dome_shutter[0].s = order_vector[0]
        dome_shutter[1].s = order_vector[1]
        self.sendNewSwitch(dome_shutter) # send this new value to the device
        time.sleep(10)

        # wait execution
        finish = False
        time_out_value = 60
        time_step = 10
        time_counter = 0
        while not self.get_shutter() == order:
            print(f"wait shutter execution time = {time_counter}   ")
            time.sleep(time_step)
            time_counter += time_step
            if time_counter > time_out_value:
                string_log = f"Dome set_shutter time out order = {order}"
                self.logger.error(string_log)
                print(string_log)
                return False

        string_log = f"dome set_shutter({order}) executed."
        self.logger.info(string_log)
        print(string_log)

        return True

    def set_azimuth(self,azimuth_order):
        print(f"dome: set azimuth to {azimuth_order}")
        self.logger.info(f"dome: set azimuth to {azimuth_order}")

        # set azimuth value
        dome_number = self.device.getNumber("HORIZONTAL_COORD")
#        for i in [0,1]:
#            print(f"dome_number[{i}] ->  name={dome_number[i].name}  value={dome_number[i].value}  " )        
        dome_number[1].value = azimuth_order
        self.sendNewNumber(dome_number)

        # wait execution
        finish = False
        angle_tolerance = 3
        time_out_value = 180
        time_step = 2
        time_counter = 0
        while not finish:
            dome_number = self.device.getNumber("HORIZONTAL_COORD")
            actual_azimuth = dome_number[1].value
            distance = abs( actual_azimuth -azimuth_order)
            print(f"wait dome rotation:  execution time = {time_counter} azimuth_order = {azimuth_order}, actual_azimuth = {actual_azimuth },  distance = {distance}")
            finish = ( distance < angle_tolerance)
            time.sleep(time_step)
            time_counter += time_step
            if time_counter > time_out_value:
                string_log = f"Dome set_azimuth time out azimuth_order = {azimuth_order}"
                self.logger.error(string_log)
                print(string_log)
                return False

        string_log = f"dome order set azimuth to {azimuth_order} degree executed."
        self.logger.info(string_log)
        print(string_log)

        return True




if __name__ == '__main__':
    
    spectro_config = os.environ['SPECTROCONFIG']
    hardware_config = json.loads(open(os.path.join(spectro_config,'hardware.json')).read())
    general_config = json.loads(open(os.path.join(spectro_config,'general.json')).read())
    
    dome_config = hardware_config['dome']
    
    # setup log file
    fileNameLog = os.path.expanduser(general_config['logFile']['indi'])
    print(f"fileNameLog = {fileNameLog}")
    logging.basicConfig(filename=fileNameLog,level=logging.DEBUG,format='%(asctime)s %(message)s')

    dome=DomeClient(dome_config)

    '''
    for i in range(3):
        dome.connect()
        print("dome connected")
        time.sleep(0.1)

        dome.disconnect()
        print("dome disconnected")
        time.sleep(0.1)
    '''


    dome.connect()

#    print(f"  dome shutter status is {dome.get_shutter()} ")
    dome.set_shutter("close")

#    time.sleep(2)
#    dome.set_azimuth(30)

    time.sleep(5)

    dome.disconnectServer()
    print("dome disconnected")

    time.sleep(2)    