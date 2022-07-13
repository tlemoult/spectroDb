import sys
from myLib.camera import CameraClient as Camera
from myLib.telescope import TelescopeClient as Telescope
import myLib.util as myUtil

import json,time,logging
import subprocess,os,sys
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.io.fits
from astropy.utils.iers import Conf as astropyConf
import numpy as np

def pointTarget(cameraGuide,telescope,J2000Target):
    global config
    
    obsSite=myUtil.getEarthLocation(config)

    fileSerie="getCoordField-"+str(loopPoint)+"-"
    pathAstrometry =  config["path"]["root"] + config["path"]["astrometry"]
    cameraGuide.newAcquSerie(pathAstrometry,fileSerie,1,cameraGuide["expTimeAstrometry"])
    cameraGuide.waitEndAcqSerie()

    filePathAstrometry = pathAstrometry + '/' + fileSerie  + "1.fits"
    astrometryResult = myUtil.solveAstro(filePathAstrometry,cameraGuide)
    if astrometryResult == None:
        print("Echec astrometry")
        return False
        
    print("syncronize telescope")
    telCoords = myUtil.convJ2000toJNowRefracted(astrometryResult["coordsJ2000"],obsSite)
    telescope.syncCoordinates(telCoords)
 
    #J2000Target = myUtil.getCoordFromName("Spica")
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
    print("  python3 pointTelescope.py configAcquire.json")
    exit()

print(f"Configuration file is {sys.argv[1]}")
config=json.loads(open(sys.argv[1]).read())
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

astropyConf.auto_download=False


catalog = { "Vega" : "18h36m56.33635s&+38d47m01.2802s" ,
    "Altair": "19h50m46.99855s&+08d52m05.9563s" ,
    "Deneb":"20h41m25.91514s&+45d16m49.2197s",
    "imgOK": "08h40m26.251922s&+36d27m00.1020804s", 
    "HD189847" : "20h00m58.74s&+31d13m49.6s",
    "HD191494": "20h08m51.8s&+36d08m46.6s",
    "NGC7027" : "21h07m01.57s&+42d14m10.47s",
    "HD199478" : "20h55m49.80s&+47d25m03.56s",  #etoile B8Iae
    "HD198478" : "20h48m56.29s&+46d06m51s" # B2.5Ia
    }

telescope=Telescope(config['telescope'])
if not telescope.connect():
    print(f"Failed to connect to telescope {config['telescope']}")
    exit()
print("Telescope connected")


# connect camera
if True:
    camera = Camera(config["ccdGuide"])
else:
    camera = Camera(config["ccdFinder"])

targetName = "HD198478"
print(f"We point the object name = {targetName}")
J2000Target = SkyCoord(catalog[targetName].replace('&',' '), frame='icrs')

for loopPoint in range(2):
    pointTarget(camera,telescope,J2000Target)

print(f"Last control before tracking")
lastcontrolExposuretime = 8
camera.newAcquSerie(config["path"]["root"] + config["path"]["astrometry"],"finalAstro-",1,lastcontrolExposuretime)
camera.waitEndAcqSerie()

###### end of the script
telescope.disconnectServer()
camera.disconnectServer()
#cameraFinder.disconnectDevice()

print(f"Wait async.. disconnect")
time.sleep(2)
