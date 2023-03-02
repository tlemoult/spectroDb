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


def syncTelescope(camera,configCamera,telescope):
    global config
    
    obsSite=myUtil.getEarthLocation(config)

    fileSerie="getCoordField-"
    pathAstrometry =  config["path"]["root"] + config["path"]["astrometry"]
    camera.newAcquSerie(pathAstrometry,fileSerie,1,configCamera["expTimeAstrometry"])
    camera.waitEndAcqSerie()

    filePathAstrometry       = pathAstrometry + '/' + fileSerie  + "1.fits"
    filePathAstrometryResize = pathAstrometry + '/' + fileSerie  + "Resize-1.fits"
    myUtil.scaleImage(filePathAstrometry,filePathAstrometryResize,configCamera["pixelSizeX"]/configCamera["pixelSizeY"])

    print("Start plate solving astrometry")
    astrometryResult = myUtil.solveAstro(filePathAstrometryResize,configCamera)
    if astrometryResult == None:
        print("Echec astrometry")
        return False
        
    actual_tel_coord = telescope.getCoordinates()
    print(f"actual telescope coordinates: ra_hms={actual_tel_coord.ra.hms}   dec_dms = {actual_tel_coord.dec.dms}")

    print("syncronize telescope")
    astrometry_tel_coordinate = myUtil.convJ2000toJNowRefracted(astrometryResult["coordsJ2000"],obsSite)
    print(f"astrometry_tel_coordinate = ra_hms={astrometry_tel_coordinate.ra.hms}   dec_dms = {astrometry_tel_coordinate.dec.dms}")
    sep = actual_tel_coord.separation(astrometry_tel_coordinate)
    print(f"sync separation is  {sep},  or {sep.arcminute} arcmin  {sep.arcsecond}  arcsecond")
    telescope.syncCoordinates(astrometry_tel_coordinate)
 
    return True


if len(sys.argv)!=2:
    print("Invalid number of argument")
    print("correct syntax is")
    print("  python syncTelescope.py finder")
    print("  python syncTelescope.py field")
    exit()

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
print(f"Configuration file is {configFilePath}")
json_text=open(configFilePath).read()
config = json.loads(json_text)

optics = sys.argv[1]
if optics == "field":
    print("We use the guiding field of spectro")
    configCamera = config["ccdGuide"]
elif optics == "finder":
    print("We use the electronic finder")
    configCamera = config["ccdFinder"]
else:
    print(f"Cannot understood the optics, argument should be finder or field")
    exit()


logging.basicConfig(filename=config["path"]["root"] + config["path"]["log"]+'/'+config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

astropyConf.auto_download=False

telescope=Telescope(config['telescope'])
if not telescope.connect():
    print(f"Failed to connect to telescope {telescope}")
    exit()
print("Telescope connected")


# connect camera

camera = Camera(configCamera)


syncTelescope(camera,configCamera,telescope)
time.sleep(0.5)

###### end of the script
telescope.disconnectServer()
camera.disconnectServer()

print(f"Wait async.. disconnect")
time.sleep(2)
