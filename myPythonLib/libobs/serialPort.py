import os,json,serial,socket
import subprocess,sys,time

spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'hardware.json')
json_text=open(configFilePath).read()
hardware_config = json.loads(json_text)


class Serial:
    def __init__(self,device,timeout=1):
        self.baud_rate = device["baud_rate"]
        self.device_type = device["type"]
        if self.device_type == "moxa_tcp":
            # init with direct tcpip socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.port = 4000+ device["port_id"]
            self.address = device["address"]
            print(f"Connect to moxa_tcp socket address = {self.address}:{self.port}")
            self.socket.connect( (self.address, self.port))

        else:
            com_device = os.path.expanduser(device["tty_path"])

            if self.device_type == "moxa_socat":
                self.ser = open_socat(device)
            else:
                self.ser = serial.Serial(com_device,self.baud_rate,timeout = timeout)

    def write(self,data):
        self.ser.write(data)
        if self.device_type == "moxa_tcp":
            self.socket.send(data)
        elif self.device_type == "moxa_socat" or self.device_type == "local":
            self.ser.write(data)
    
    def readline(self):
        if self.device_type == "moxa_tcp":
            x = self.socket.makefile("rb")
            return x.readline()
        elif self.device_type == "moxa_socat" or self.device_type == "local":
            return self.ser.readline()

    def flush(self):
        if self.device_type == "moxa_socat" or self.device_type == "local":
            self.ser.flush()
    
    def close(self):
        if self.device_type == "moxa_tcp":
            self.socket.close()
        elif self.device_type == "moxa_socat" or self.device_type == "local":
            self.ser.close()




def open_socat(deviceName,timeout=1):
    serial_config = hardware_config[deviceName]['serial_port']
    tty_path_global = os.path.expanduser(serial_config['tty_path'])
    print(f"com_port_url = {tty_path_global}")
    try:
        ser = serial.Serial(tty_path_global,serial_config["baud_rate"],timeout=timeout)
        print(f"Success in open com port {tty_path_global}")
        return ser
    except serial.serialutil.SerialException:
        print("Failed to open, we probably need to lunch socat tunnel..")
        create_socat(deviceName)

    try:
        print("Retry open device after socat")
        ser = serial.Serial(tty_path_global,serial_config["baud_rate"],timeout=timeout)
        print(f"Success in open com port {tty_path_global}")
        return ser
    except serial.serialutil.SerialException:
        print("Failed to open, probably incorrect configuration or device is off.")
        return None

def create_socat(deviceName):
    print(f"Try to open with socat the device {deviceName}")

    serial_config = hardware_config[deviceName]['serial_port']
    server_address = serial_config['address']
    tcp_port = 4000 + serial_config['port_id']
    tty_path_global = os.path.expanduser(serial_config['tty_path'])

    print(f"socat.create() pipe {tty_path_global} <-> {server_address}:{tcp_port}")
    socat_cmd = f"socat pty,link={tty_path_global},group-late=dialout,mode=660  tcp:{server_address}:{tcp_port} &"
    print(f"call {socat_cmd}")
    try:
        retcode = subprocess.call(socat_cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
    time.sleep(1)


def main():
    print("test for serial Port")

    ser = open_socat("eShel")

if __name__ == "__main__":
    main()	
