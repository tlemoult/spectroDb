import sys,time, logging,json
import PyIndi

from lib.CamSpectro import IndiClient as CamSpectro

#load configuration
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
# instantiate the client, for camera
camSpectro=CamSpectro(config['ccdSpectro']['name'])
# set indi server
server=config['ccdSpectro']['server']
camSpectro.setServer(str(server['host']),server['port'])
# connect to indi server
print("Connecting and waiting 2secs")
if (not(camSpectro.connectServer())):
     print("No indiserver running on "+camSpectro.getHost()+":"+str(camSpectro.getPort())+" - Try to run")
     print("  indiserver indi_simulator_ccd")
     sys.exit(1)
time.sleep(2)

#set binning
camSpectro.setBinning(config['ccdSpectro']['binning'])
#set temperature of CCD
print("setTemperature")
camSpectro.setTemperature(config['ccdSpectro']['tempSetPoint'])
camSpectro.waitCCDTemperatureOK()

#acquisition
print "run acquisition" 
camSpectro.newAcquSerie(config['path']['acquire'],"OBJECT-",3,1)
camSpectro.waitEndAcqSerie()

print("acquisition finished")
