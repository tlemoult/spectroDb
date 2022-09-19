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

def syncTelescope(camera,configCamera,telescope):
    global config
    
    obsSite=myUtil.getEarthLocation(config)

    fileSerie="getCoordField-"
    pathAstrometry =  config["path"]["root"] + config["path"]["astrometry"]
    camera.newAcquSerie(pathAstrometry,fileSerie,1,configCamera["expTimeAstrometry"])
    camera.waitEndAcqSerie()

    filePathAstrometry = pathAstrometry + '/' + fileSerie  + "1.fits"
    astrometryResult = myUtil.solveAstro(filePathAstrometry,configCamera)
    if astrometryResult == None:
        print("Echec astrometry")
        return False
        
    print("syncronize telescope")
    telCoords = myUtil.convJ2000toJNowRefracted(astrometryResult["coordsJ2000"],obsSite)
    telescope.syncCoordinates(telCoords)
 
    return True


if len(sys.argv)!=2:
    print("Invalid number of argument")
    print("correct syntax is")
    print("  python3 syncTelescope.py configAcquire.json")
    exit()

print(f"Configuration file is {sys.argv[1]}")
config=json.loads(open(sys.argv[1]).read())
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

astropyConf.auto_download=False

telescope=Telescope(config['telescope'])
if not telescope.connect():
    print(f"Failed to connect to telescope {telescope}")
    exit()
print("Telescope connected")


# connect camera
if False:
    configCamera = config["ccdGuide"]
else:
    configCamera = config["ccdFinder"]

camera = Camera(configCamera)


syncTelescope(camera,configCamera,telescope)

###### end of the script
telescope.disconnectServer()
camera.disconnectServer()

print(f"Wait async.. disconnect")
time.sleep(2)
