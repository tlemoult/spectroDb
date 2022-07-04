import sys,time, logging,json
import PyIndi

from myLib.camera import CameraClient as CamSpectro

#load configuration
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
# create and connect to Camera 
camSpectro=CamSpectro(config["ccdSpectro"])

#acquisition
print("run acquisition")
camSpectro.newAcquSerie(config['path']['acquire'],"OBJECT-",3,10)
camSpectro.waitEndAcqSerie()

print("acquisition finished")
