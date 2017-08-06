import os,sys,time, datetime,logging,json
import PyIndi

from lib.CamSpectro import IndiClient as CamSpectro


n=len(sys.argv)
print "n=",n
print sys.argv
if n!=6:
    print "syntaxe:"
    print '    python acquire.py "Project" target "OBJ NAME" nbExposure expTime'
    print 'exemple:'
    print '    python acquire.py "none"   obj "HD2203"   3           600'
    print '    python acquire.py "none"   ref "HD103"   3           600'
    exit()
else:
    projectName=sys.argv[1].split('"')[0]
    print "projectName=",projectName
    objTypeArg=sys.argv[2]
    print "objType=",objTypeArg
    objName=sys.argv[3].split('"')[0]
    print "objName=",objName
    nbExposure=int(sys.argv[4])
    print "nbExposure=",nbExposure
    expTime=float(sys.argv[5])
    print "expTime=",expTime

#load configuration
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

#create directory
basePath=config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').split('.')[0]
basePath+='-'+objName.replace(' ','_').replace('+','p').replace('*','s')
print "basePath=",basePath
os.mkdir(basePath)

#create observation.json
observationJson=config['templateObservation']
observationJson['target']['objname']=[objName]
observationJson['target']['isRef']=(objTypeArg=='ref')
observationJson['project']=projectName
observationJson['target']['coord']['ra']=""
observationJson['target']['coord']['dec']=""
observationJson['statusObs']="started"
observationJson['obsConfig']['NbExposure']=nbExposure
observationJson['obsConfig']['ExposureTime']=expTime
observationJson['obsConfig']['TotalExposure']=nbExposure*expTime

with open(basePath+'/observation.json', 'w') as outfile:
    json.dump(observationJson, outfile)

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

#acquisition
print "run acquisition" 
camSpectro.newAcquSerie(basePath,"OBJECT-",nbExposure,expTime)
camSpectro.waitEndAcqSerie()

raw_input('Switch on Neon, Press enter to continue: ')
camSpectro.newAcquSerie(basePath,"NEON-",1,5)
camSpectro.waitEndAcqSerie()

#update json file
observationJson['obsConfig']['NbExposure']=nbExposure
observationJson['obsConfig']['ExposureTime']=expTime
observationJson['obsConfig']['TotalExposure']=nbExposure*expTime
observationJson['statusObs']="finished"
with open(basePath+'/observation.json', 'w') as outfile:
    json.dump(observationJson, outfile)

print("acquisition finished")

raw_input('Switch off Neon, Press enter to continue: ')
