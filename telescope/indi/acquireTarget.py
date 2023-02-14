import os,sys,time, datetime,logging,json
import PyIndi

from libindi.camera import CameraClient as CamSpectro
import libobs.powerControl as powerControl

n=len(sys.argv)

if n!=6:
    print("syntaxe:")
    print('    python acquire.py  "Project" target "OBJ NAME" nbExposure expTime')
    print('exemple:')
    print('    python acquire.py  "none"   obj "HD2203"   3           600')
    print('    python acquire.py  "none"   ref "HD103"   3           600')
    exit()


projectName=sys.argv[1].split('"')[0]
print(f"projectName={projectName}")
objTypeArg=sys.argv[2]
print(f"objType={objTypeArg}")
objName=sys.argv[3].split('"')[0]
print(f"objName={objName}")
nbExposure=int(sys.argv[4])
print(f"nbExposure={nbExposure}")
expTime=float(sys.argv[5])
print(f"expTime={expTime}")

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

#create directory
basePath=config['path']['root']+'/'+config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').replace(':','-').split('.')[0]
basePath+='-'+objName.replace(' ','_').replace('+','p').replace('*','s')
print(f"basePath={basePath}")
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

camSpectro=CamSpectro(config["ccdSpectro"])
camSpectro.setObserverAndObjectName(observationJson['observer']['alias'],objName)
print("run acquisition" )
camSpectro.newAcquSerie(basePath,"OBJECT"+"-",nbExposure,expTime)
camSpectro.waitEndAcqSerie()
print("  acquisition finished")

print('Switch on the NEON lamp')
relay_calib_neon = 5
powerControl.set(relay_calib_neon,True)

spectroCalib=config['spectro']['LISA']['calib']
camSpectro.newAcquSerie(basePath,"NEON-",spectroCalib['nbExpo'],spectroCalib['exposure'])
camSpectro.waitEndAcqSerie()

#update json file
observationJson['obsConfig']['NbExposure']=nbExposure
observationJson['obsConfig']['ExposureTime']=expTime
observationJson['obsConfig']['TotalExposure']=nbExposure*expTime
observationJson['statusObs']="finished"
with open(basePath+'/observation.json', 'w') as outfile:
    json.dump(observationJson, outfile, indent = 4)

print("acquisition finished")

print('Switch off Neon')
powerControl.set(relay_calib_neon,False)
camSpectro.disconnectServer()

print(f"Wait disconnection...")
time.sleep(5)
