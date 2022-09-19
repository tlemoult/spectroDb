import serial,os,time

comDevice = os.path.expanduser("~/.local/dev/ttyEshel")

# param is one "off","led","flat","calib"
def _send(param):
	start=13
	adress=1
	command=ord('B')
	checkSum=256-((adress+start+command+param) % 256)
	cmd=[start,adress,command,param,checkSum]
	print("send data to eShell calibration module")
	print(f"decimal cmd = {cmd}")
	bytesCmd = bytes(cmd)
	print(f"byteCmd = {bytesCmd}")
	print(f"Open serial port {comDevice}")
	ser = serial.Serial(comDevice,2400,timeout=1)
	ser.write(bytesCmd)
	ser.flush()
	ser.close()

def set(state):
	miror=0b10000000
	led=0b01000000
	thAr=0b00100000
	tungsten=0b00010000
	cmd_dict={'led':miror+led+tungsten,'off':0,'calib':miror+thAr,'flat':miror+tungsten}
	
	if state in cmd_dict.keys():
		_send(cmd_dict[state])
		print(f"Success set eShel Calib to {state}")
		return True
	else:
		print(f"Failed set eShel Calib to {state}")
		return False

