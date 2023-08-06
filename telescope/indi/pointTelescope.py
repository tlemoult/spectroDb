import sys
from libindi.camera import CameraClient as Camera
from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil

import json,time,logging
import subprocess,os,sys
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.io.fits
from astropy.utils.iers import Conf as astropyConf
import numpy as np

def pointTarget(cameraGuide,cameraConfig,telescope,J2000Target):
    global config
    
    obsSite=myUtil.getEarthLocation(config)

    fileSerie="getCoordField-"+str(loopPoint)+"-"
    pathAstrometry =  config["path"]["root"] + config["path"]["astrometry"]
    cameraGuide.newAcquSerie(pathAstrometry,fileSerie,1,cameraConfig["expTimeAstrometry"])
    cameraGuide.waitEndAcqSerie()

    filePathAstrometry = pathAstrometry + '/' + fileSerie  + "1.fits"
    filePathAstrometryResize = pathAstrometry + '/' + fileSerie  + "Resize-1.fits"
    myUtil.scaleImage(filePathAstrometry,filePathAstrometryResize,configCamera["pixelSizeX"]/configCamera["pixelSizeY"])

    astrometryResult = myUtil.solveAstro(filePathAstrometryResize,cameraConfig)
    if astrometryResult == None:
        print("Echec astrometry")
        return False
        
    print("syncronize telescope")
    telCoords = myUtil.convJ2000toJNowRefracted(astrometryResult["coordsJ2000"],obsSite)
    telescope.syncCoordinates(telCoords)
 
    
    obsSite=myUtil.getEarthLocation(config)
    CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)
    telescope.slewTelescope(CoordTelescopeTarget)
    delayAfterSlew = config["telescope"]["delayAfterSlew"]
    print(f"Wait {delayAfterSlew} seconds after slew...")
    time.sleep(delayAfterSlew)

    return True

if len(sys.argv)!=2:
    print("Invalid number of argument")
    print("correct syntax is")
    print("  python pointTelescope.py target")
    exit()

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
print(f"Configuration file is {configFilePath}")
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logFilePath = config['path']['root']+config['path']['log']+'/'+config['logFile']
print(f"{logFilePath=}")
logging.basicConfig(filename=logFilePath,level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

astropyConf.auto_download=False

# idea for ref star list:  
# CDS SIMBAD: sptypes in ('A0','A1','A2','A4','A5') & Vmag > 3 & Vmag <9 & region(CIRCLE,21 37 +30,20)

catalog = { "Vega" : "18h36m56.33635s&+38d47m01.2802s" ,
    "Altair": "19h50m46.99855s&+08d52m05.9563s" ,
    "Deneb":"20h41m25.91514s&+45d16m49.2197s",
    "imgOK": "08h40m26.251922s&+36d27m00.1020804s", 
    "HD189847" : "20h00m58.74s&+31d13m49.6s",
    "HD191494": "20h08m51.8s&+36d08m46.6s",
    "NGC7027" : "21h07m01.57s&+42d14m10.47s",
    "HD199478" : "20h55m49.80s&+47d25m03.56s",  #etoile B8Iae
    "HD198478" : "20h48m56.29s&+46d06m51s", # B2.5Ia
    "TYC 2717-453-1" : "21h38m21.99s&+30d33m22s", # variable a caracteriser
    "HD207469" : "21h48m23.51s&+32d47m46s", # ref star  A0
    "HD203286" : "21h20m20.54s&+33d29m07s" # ref star A0
    }

telescope=Telescope(config['telescope'])
if not telescope.connect():
    print(f"Failed to connect to telescope {config['telescope']}")
    exit()
print("Telescope connected")


# connect camera
if False:
    print("We use the guiding field of spectro")
    configCamera = config["ccdGuide"]
else:
    print("We use the electronic finder")
    configCamera = config["ccdFinder"]

print(f"camera is {configCamera['name']}")
camera = Camera(configCamera)


targetName = sys.argv[1]
if targetName in catalog.keys():
    J2000Target = SkyCoord(catalog[targetName].replace('&',' '), frame='icrs')
else:
    J2000Target = myUtil.getCoordFromName(targetName)
print(f"We point the object name = {targetName}  coord J2000 = {J2000Target}")


for loopPoint in range(2):
    pointTarget(camera,configCamera,telescope,J2000Target)

print(f"Last control before tracking")
lastcontrolExposuretime = 8
camera.newAcquSerie(config["path"]["root"] + config["path"]["astrometry"],"finalAstro-",1,lastcontrolExposuretime)
camera.waitEndAcqSerie()

###### end of the script
telescope.disconnectServer()
camera.disconnectServer()


print(f"Wait async.. disconnect")
time.sleep(2)
