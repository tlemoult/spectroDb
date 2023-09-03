import sys,time, logging,json,os
import PyIndi

from libindi.camera import CameraClient as CamSpectro

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
print(f"load configuration {configFilePath=}")
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logFilePath = config['path']['root']+config['path']['log']+'/'+config['logFile']
print(f"{logFilePath=}")
logging.basicConfig(filename=logFilePath,level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

# create and connect to Camera 
camSpectro=CamSpectro(config["ccdSpectro"])

#acquisition
print("run acquisition")
camSpectro.newAcquSerie(config['path']['acquire'],"OBJECT-",3,10)
camSpectro.waitEndAcqSerie()

print("acquisition finished")
