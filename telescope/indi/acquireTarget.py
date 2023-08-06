import os,sys,time, datetime,logging,json
import PyIndi

from libindi.camera import CameraClient as CamSpectro
from libindi.telescope import TelescopeClient as Telescope
from libcalc.img import statSpectrum
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
print("Acquire Target spectrum")
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
print(f"load configuration {configFilePath=}")
json_text=open(configFilePath).read()
config = json.loads(json_text)
CalibManual = True

# setup log file
logFilePath = config['path']['root']+config['path']['log']+'/'+config['logFile']
print(f"{logFilePath=}")
logging.basicConfig(filename=logFilePath,level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

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

# get Telescope Coordinates
telescope=Telescope(config['telescope'])
print(f"try to connect to {config['telescope']['name']}")
if not telescope.connect():
    print("Failed to connect to telescope")
    exit(1)

telescopeCoords = telescope.getCoordinates()

# instantiate the client, for camera

camSpectro=CamSpectro(config["ccdSpectro"])
camSpectro.setAdditionnalFitsKeyword("OBSERVER",observationJson['observer']['alias'])
camSpectro.setAdditionnalFitsKeyword("BSS_SITE",observationJson['site']['name'])
camSpectro.setAdditionnalFitsKeyword("OBJNAME",objName,comment='Simbad object name')
camSpectro.setAdditionnalFitsKeyword("CRVAL1",telescopeCoords.ra.deg,comment='approx RA in degree')
camSpectro.setAdditionnalFitsKeyword("CRVAL2",telescopeCoords.dec.deg,comment='approx DEC in degree')
print(f"run acquisition with camera {config['ccdSpectro']['name']}" )
camSpectro.newAcquSerie(basePath,"OBJECT"+"-",nbExposure,expTime,display_spectrum=True)
camSpectro.waitEndAcqSerie()
print("  acquisition finished")

print('Switch on the NEON lamp')
relay_calib_neon = 5
if CalibManual:
    input("press Enter when done")
else:
    powerControl.set(relay_calib_neon,True)

spectroName = config['spectro']['selected']
print(f"{spectroName=}")
for spectroCalib in config['spectro'][spectroName]['calib']:
    camSpectro.newAcquSerie(basePath,spectroCalib['serieName'],spectroCalib['nbExpo'],spectroCalib['exposure'])
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
if CalibManual:
    input("press Enter when done")
else:
    powerControl.set(relay_calib_neon,False)
camSpectro.disconnectServer()

print(f"Wait disconnection...")
time.sleep(5)
