import sys
sys.path.append("..")
from libindi.camera import CameraClient as CamSpectro
from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil

from flask import Flask, jsonify, abort, make_response, request
import json,time,logging
import subprocess,os,sys
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import astropy.io.fits
from astropy.utils.iers import Conf as astropyConf
import numpy as np

app = Flask(__name__)



def stackSerie(sourcePath,nbImage):
    print("stackSerie()")
    fileNamePath=os.path.split(sourcePath)[0]
    fileNameRoot=os.path.split(sourcePath)[1].split('.')[0]
    fileNameImage=fileNamePath+'/'+fileNameRoot+"-1.fits"
    print(f"  fileNamePath = {fileNamePath}")
    print(f"  fileNameRoot = {fileNameRoot}")
    print(f"  fileNameImage = {fileNameImage}")

    hdul = astropy.io.fits.open(fileNameImage)
    hdu = hdul[0]
    imgStack = np.float64(hdu.data)
    print(f"  open {fileNameImage} EXPTIME = {hdu.header['EXPTIME']}")
    myHeader = hdu.header
    expTime = hdu.header['EXPTIME']
    hdul.close()

    for i in range(1,nbImage):
        fileNameImage=fileNamePath+'/'+fileNameRoot+"-"+str(i+1)+".fits"
        hdul = astropy.io.fits.open(fileNameImage)
        hdu = hdul[0]
        expTime = expTime + hdu.header['EXPTIME']
        print(f"  open {fileNameImage} EXPTIME = {hdu.header['EXPTIME']}")
        imgStack = imgStack + hdu.data
        hdul.close()

    imgStack = imgStack / nbImage
    
    hdu = astropy.io.fits.PrimaryHDU(imgStack)
    hdu.header = myHeader
    myHeader['EXPTIME'] = expTime
    fileNameImage = fileNamePath+'/'+fileNameRoot+".fits"
    print(f"  Save staked image to {fileNameImage} total EXPTIME = {expTime}")
    try:
        os.remove(fileNameImage)
    except:
        print(f"  no previous stack file {fileNameImage}")

    hdu.writeto(fileNameImage)

def substrackFits(fileName1,fileName2,fileNameDest):
    print("subStrackFits()")
    print(f"  Write ({fileNameDest}) with ({fileName1})-({fileName2})")
    hdul1 = astropy.io.fits.open(fileName1)
    hdu1 = hdul1[0]
    img1 = hdu1.data

    hdul2 = astropy.io.fits.open(fileName2)
    hdu2 = hdul2[0]
    img2 = hdu2.data
    
    destData= img1 - img2

    hdu = astropy.io.fits.PrimaryHDU(destData)
    hdu.header = hdu1.header
    try:
        os.remove(fileNameDest)
    except:
        print(f"  no previous dest File {fileNameDest}")
    hdu.writeto(fileNameDest)

    hdul1.close()
    hdul2.close()

# called by API
def doAcquireOffset(config):
    print("doAcquireOffset()")
    
    fileNamePath=os.path.split(config["path"]["offset"])[0]
    print(f"  fileNamePath = {fileNamePath}")
    fileNameRoot=os.path.split(config["path"]["offset"])[1].split('.')[0]
    print(f"  fileNameRoot = {fileNameRoot}")

    exposureTime = 0

    camSpectro=CamSpectro(config["camera"])    
    camSpectro.newAcquSerie(fileNamePath,fileNameRoot+"-",config["calib"]["nbExposure"],config["calib"]["exposureTime"])
    camSpectro.waitEndAcqSerie()

    print("  acquisition finished")
    camSpectro.disconnectServer()

    stackSerie(config["path"]["offset"],config["calib"]["nbExposure"])
    
    return {"protoVersion":"1.00", "calib":"done"}

# called by API
def doFinderSolveAstro(config):
    print("doFinderSolveAstro()")
    ### Picture acquisition with Finder Scope
    if config['testWithoutSky']:
        #False image
        fileNameAstro=config["imageTest"]
        print(f"  Test without sky, use {fileNameAstro}")
        time.sleep(2)
    else:
        #Real image on the sky
        fileNamePath=os.path.split(config["path"]["image"])[0]
        print(f"    fileNamePath = {fileNamePath}")        
        fileNameRoot=os.path.split(config["path"]["image"])[1].split('.')[0]
        print(f"    fileNameRoot = {fileNameRoot}")
              
        #acquisition
        print("  run acquisition")
        camSpectro=CamSpectro(config["camera"])
        camSpectro.newAcquSerie(fileNamePath,fileNameRoot+"-",config["acquisition"]["nbExposure"],config["acquisition"]["exposureTime"])
        camSpectro.waitEndAcqSerie()
        print("  acquisition finished")
        camSpectro.disconnectServer()
    
        fileNameImage=config["path"]["image"]
        stackSerie(fileNameImage,config["acquisition"]["nbExposure"])
        
        fileNameAstro = fileNameImage.replace(".fits","-Astro.fits")
        print(f"  fileNameAstro = {fileNameAstro}")
        substrackFits(fileNameImage,config["path"]["offset"],fileNameAstro)

#    return {"debug":"true"}

    ### Plate Solving
     
    
    astro = myUtil.solveAstro(fileNameAstro,config["camera"])

    if astro == None:
        print("error during plate solving...")
        print("Unexpected error:", sys.exc_info()[0])
        abort(500,description='plate solving')
        return { 'error':'error' }

   # astrometry = {"wcs":wcs,  "raStr":raStr , "decStr":decStr , "coordsJ2000":coordsJ2000 ,"wx":wx , "wy",wy  }

    ### send coord to telescope
    telescope=Telescope(config['telescope'])

    if telescope.connect():
        print("Telescope connected")
        obsSite=myUtil.getEarthLocation(config)
        telCoords = myUtil.convJ2000toJNowRefracted(astro["coordsJ2000"],obsSite)
        telescope.syncCoordinates(telCoords)
        telescope.disconnectServer()
        time.sleep(2)
    else:
        print("Cannot connect telescope {config['telescope']}")

    pi = 3.141592653589793
    result= { 'protoVersion':'1.00', 'coord': {'RA': str(astro["wx"]/180.0*pi), 'DEC':str(astro["wy"]/180.0*pi) , 'unit':'RADIAN', 'EPOCH':'J2000'} , 'coorSEX': {'RA':astro["raStr"], 'DEC':astro["decStr"], 'EPOCH':'J2000'}}
    print(result)

    return result

# called by API
def doFinderSetCenter(config,coords):
    print ("Enter dofinderSetCenter()")
    alpha, delta = coords.split('&')
    print (f"   The real optical center is at: J2000 alpha = {alpha}  delta = {delta}")
    
    fileNameAstro = config["path"]["image"].replace(".fits","-Astro.fits")
    name, extension = os.path.splitext(fileNameAstro)
    print(f"   reload astrometry data from {name}")
    wcs = astropy.wcs.WCS(astropy.io.fits.open(name+'.wcs')[0].header)

    sky  = SkyCoord(alpha,delta,frame = 'icrs')
    fenteXpix, fenteYpix =(sky.to_pixel(wcs))
    
    fenteXpix = float(fenteXpix)
    fenteYpix = float(fenteYpix)
    deltaXpix , deltaYpix = fenteXpix-config['camera']['centerX'] , fenteYpix-config['camera']['centerY']
    config['camera']['centerX']= fenteXpix
    config['camera']['centerY']= fenteYpix

    #write to config file here ??
  
    result = { 'newCenter' : {'x': fenteXpix , 'y':fenteYpix} , 'deltaCenter': {'x':deltaXpix, 'y':deltaYpix} }
    print(f"   result={result}")
    return result

############ main ###############
@app.route('/api/finder/setCenter', defaults = {'coords': 'none'})
@app.route('/api/finder/setCenter/<coords>', methods=['GET'])
def setCenter(coords):
    global config
    if coords == 'none':
        return "This will set the X,Y optical center configuration.\nYou must use as argument the J2000 coordinates for this API\n" + "example:    http://localhost:5000/api/finder/setCenter/14h25m45.6s&+65d11m"
    if not '&' in coords:
        return f"argument must contains & to separate alpha&delta \n argument is {coords}"

    return jsonify(doFinderSetCenter(config,coords))

@app.route('/api/finder/acquireOffset', methods=['GET'])
def acquireOffset():
    global config
    return jsonify(doAcquireOffset(config))

@app.route('/api/finder', methods=['GET'])
def get_finder():
    global config
    return jsonify(doFinderSolveAstro(config))

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print("Invalid number of argument")
        print("correct syntax is")
        print("  python3 apiFinder.py configAutoSolver.json")
        exit()

    else:
        print(f"Confirguration file is {sys.argv[1]}")
        config=json.loads(open(sys.argv[1]).read())
        logging.basicConfig(filename=config['path']['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

        astropyConf.auto_download=False
        
        
        app.run(host='0.0.0.0',port=5000,debug=True)

