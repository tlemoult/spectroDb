import os,sys,time, datetime,logging,json
import PyIndi

from lib.CamSpectro import IndiClient as CamSpectro




#load configuration
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

# instantiate the client, for camera
camSpectro=CamSpectro(config['ccdFinder']['name'])
# set indi server
server=config['ccdFinder']['server']
camSpectro.setServer(str(server['host']),server['port'])
# connect to indi server
print("Connecting and waiting 2secs")
if (not(camSpectro.connectServer())):
     print("No indiserver running on "+camSpectro.getHost()+":"+str(camSpectro.getPort())+" - Try to run")
     print("  indiserver indi_simulator_ccd")
     sys.exit(1)
time.sleep(3)

#acquisition
print("run acquisition") 
expTime=10
basePath="."
camSpectro.newAcquSerie(basePath,"FINDER-",1,expTime)
camSpectro.waitEndAcqSerie()

print("acquisition finished")

