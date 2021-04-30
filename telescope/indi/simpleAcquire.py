import sys,time, logging,json
import PyIndi

from lib.CamSpectro import IndiClient as CamSpectro

#load configuration
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
# create Camera Client
camSpectro=CamSpectro(config['ccdSpectro']['name'],config['ccdSpectro']['server']['host'],config['ccdSpectro']['server']['port'])
print("Connecting to indiserver")
if (not(camSpectro.connectServer())):
     print(f"Fail to connect to indi Server {camSpectro.getHost()}:{camSpectro.getPort()}")
     print("Try to run:")
     print("  indiserver indi_simulator_ccd")
     sys.exit(1)

print("connecting to camera")
if (not(camSpectro.waitCameraConnected())):
     print("Fail to connect to camera")
     sys.exit(1)

#set binning
camSpectro.setBinning(config['ccdSpectro']['binning'])
#set temperature of CCD
if True:
     print("setTemperature")
     camSpectro.setTemperature(config['ccdSpectro']['tempSetPoint'])
     camSpectro.waitCCDTemperatureOK()

#acquisition
print("run acquisition")
camSpectro.newAcquSerie(config['path']['acquire'],"OBJECT-",3,10)
camSpectro.waitEndAcqSerie()

print("acquisition finished")
