import os,sys,time, datetime,logging,json
import PyIndi

from libindi.camera import CameraClient as CamSpectro
import libobs.powerControl as powerControl

print("Sample command:  python acquireCalibNeonFlat.py flat neon")
n=len(sys.argv)
if n == 1:
    calib = ["neon", "flat"]
else:
    calib = sys.argv[1:n]

print(f"calib = {calib}")

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

# instantiate the client, for camera
camSpectro=CamSpectro(config["ccdSpectro"])

#create directory
basePath=config['path']['root']+'/'+config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').replace(':','-').split('.')[0]
basePath+='-'+"NeonFlat"
print(f"basePath={basePath}")
os.mkdir(basePath)

if 'neon' in calib:
    print('Switch on the NEON lamp')
    relay_calib_neon = 5
    powerControl.set(relay_calib_neon,True)
    spectroCalib=config['spectro']['LISA']['calib']
    camSpectro.newAcquSerie(basePath,"neon-",spectroCalib['nbExpo'],spectroCalib['exposure'])
    camSpectro.waitEndAcqSerie()
    print("  acquisition finished")
    powerControl.set(relay_calib_neon,False)

if 'flat' in calib:
    print('Switch on the flat lamp')
    relay_flat_lamp = 6
    powerControl.set(relay_flat_lamp,True)
    spectroFlat=config['spectro']['LISA']['flat']
    camSpectro.newAcquSerie(basePath,"flat-",spectroFlat['nbExpo'],spectroFlat['exposure'])
    camSpectro.waitEndAcqSerie()
    print("  acquisition finished")
    powerControl.set(relay_flat_lamp,False)

camSpectro.disconnectServer()

time.sleep(2)
