import os,sys,time, datetime,logging,json
import PyIndi

from libindi.camera import CameraClient as CamSpectro
import libobs.powerControl as powerControl


#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

#create directory
basePath=config['path']['root']+'/'+config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').replace(':','-').split('.')[0]
basePath+='-'+"calibCCD"
print(f"basePath={basePath}")
os.mkdir(basePath)

# instantiate the client, for camera
camSpectro=CamSpectro(config["ccdSpectro"])


if False:
    print("flat Acquisition" )
    print('Switch on the NEON lamp')
    relay_flat_lamp = 6
    powerControl.set(relay_flat_lamp,True)

    spectroFlat=config['spectro']['LISA']['flat']
    camSpectro.newAcquSerie(basePath,"flat-",spectroFlat['nbExpo'],spectroFlat['exposure'])
    camSpectro.waitEndAcqSerie()
    print("  acquisition finished")

    print('Switch off the Flat lamp')
    powerControl.set(relay_flat_lamp,True)

    input('Put camera in the dark condition...., Press enter to continue: ')


print("Offset Acquisition" )
camSpectro.newAcquSerie(basePath,"offset-",15,0.1)
camSpectro.waitEndAcqSerie()
print("  acquisition finished")


print("Dark Acquisition")
camSpectro.newAcquSerie(basePath,"dark-",7,300)
camSpectro.waitEndAcqSerie()


print("acquisition finished")


camSpectro.disconnectServer()

time.sleep(2)
