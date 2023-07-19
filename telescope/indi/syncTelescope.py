import sys
from libindi.camera import CameraClient as Camera
from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil

import json,time,logging
import subprocess,os,sys
from astropy import units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.io.fits
from astropy.utils.iers import Conf as astropyConf
import numpy as np

def coord_to_str(coords):
    raStr = str(coords.ra.to_string(u.hour,precision=2))
    decStr = str(coords.dec.to_string(u.degree, alwayssign=True,precision=2))
    return f"{raStr} {decStr}"

def syncTelescope(camera,configCamera,telescope,realCoord=None):
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
    astrometryResult = myUtil.solveAstro(filePathAstrometryResize,configCamera,realCoord)
    if astrometryResult == None:
        print("Echec astrometry")
        return False
        
    actual_tel_coord = telescope.getCoordinates()
    print(f"astrometry result {astrometryResult}")
    print(f"actual telescope JNOW apparent: {coord_to_str(actual_tel_coord)}")

    J2000_astrometry = astrometryResult["coordsJ2000"]
    astrometry_tel_coordinate = myUtil.convJ2000toJNowRefracted(J2000_astrometry,obsSite)
     
    print(f'astrometry result in J2000 {coord_to_str(J2000_astrometry)}')
    print(f"astrometry result JNOW apparent {coord_to_str(astrometry_tel_coordinate)}")
    sep = actual_tel_coord.separation(astrometry_tel_coordinate)
    print(f"sync separation is  {sep},  or {sep.arcminute} arcmin  {sep.arcsecond}  arcsecond")

    print("syncronize telescope")
    telescope.syncCoordinates(astrometry_tel_coordinate)

    return True


if len(sys.argv) < 2:
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

if len(sys.argv) == 3:
    realStarName = sys.argv[2]
    realCoord = myUtil.getCoordFromName(realStarName)
    print(f"realStarName = {realStarName}  realCoord = {coord_to_str(realCoord)}")
else:
    realCoord = None

logging.basicConfig(filename=config["path"]["root"] + config["path"]["log"]+'/'+config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

astropyConf.auto_download=False

telescope=Telescope(config['telescope'])
if not telescope.connect():
    print(f"Failed to connect to telescope {telescope}")
    exit()
print("Telescope connected")


# connect camera

camera = Camera(configCamera)


syncTelescope(camera,configCamera,telescope,realCoord=realCoord)
time.sleep(0.5)

###### end of the script
telescope.disconnectServer()
camera.disconnectServer()

print(f"Wait async.. disconnect")
time.sleep(2)
