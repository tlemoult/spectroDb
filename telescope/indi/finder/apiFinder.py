import sys
sys.path.append("..")
from myLib.camera import CameraClient as CamSpectro

from flask import Flask, jsonify, abort, make_response
import json,time,logging
import subprocess,os,sys
from astropy.wcs import WCS
import astropy.io.fits
import numpy as np

app = Flask(__name__)

def solveAstro(filename,scale):
    print("debut resolution astrometrique ",scale,"arcsec per pixel, file=",filename)
    name, extension = os.path.splitext(filename)
    scale_low = str(scale*80.0/100.0)
    scale_high = str(scale*120.0/100.0)
    subprocess.call(["/usr/bin/solve-field","--cpulimit","12","--downsample", "2", "--tweak-order", "2", "--scale-units", "arcsecperpix", "--scale-low", scale_low, "--scale-high", scale_high, "--no-plots", "--overwrite", filename])
    if os.path.isfile(name+'.solved'):
        print("succes resolution astrometrique, get wcs data")
        wcs = astropy.wcs.WCS(astropy.io.fits.open(name+'.wcs')[0].header)

        try:
            os.remove(name+'-indx.xyls')
            os.remove(name+'.axy')
            os.remove(name+'.corr')
            os.remove(name+'.match')
            os.remove(name+'.new')
            os.remove(name+'.rdls')
            os.remove(name+'.solved')
            os.remove(name+'.wcs')
        except:
            print("    Some file was not here.")

        return wcs

    else:
        print("echec resolution astrometrique")
        raise

def connectCam(config):
    # acquisition of picture thru INDI server
    camSpectro=CamSpectro(config["camera"]["name"],config["camera"]["indiServerAddress"],config["camera"]["indiServerPort"])
        
    print("Connecting to indiserver")
    if (not(camSpectro.connectServer())):
        print(f"Fail to connect to indi Server {camSpectro.getHost()}:{camSpectro.getPort()}")
        print("Try to run:")
        print("  indiserver indi_simulator_ccd")
        abort(500,description="Fail to connect to indi Server")

    print("connecting to camera")
    if (not(camSpectro.waitCameraConnected())):
        print("Fail to connect to camera")
        camSpectro.disconnectServer()
        abort(500,description="Fail to connect to camera")

    #set binning    
    camSpectro.setBinning({'X':config["camera"]["binning"],'Y':config["camera"]["binning"]})
    
    return camSpectro

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
def doFinderCalib(config):
    print("doFinderCalib()")
    
    fileNamePath=os.path.split(config["path"]["offset"])[0]
    print(f"  fileNamePath = {fileNamePath}")
    fileNameRoot=os.path.split(config["path"]["offset"])[1].split('.')[0]
    print(f"  fileNameRoot = {fileNameRoot}")

    exposureTime = 0

    camSpectro = connectCam(config)    
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
        print(f"  Test without sky, use {fileNameImage}",fileNameImage)
        time.sleep(2)
    else:
        #Real image on the sky
        fileNamePath=os.path.split(config["path"]["image"])[0]
        print(f"    fileNamePath = {fileNamePath}")        
        fileNameRoot=os.path.split(config["path"]["image"])[1].split('.')[0]
        print(f"    fileNameRoot = {fileNameRoot}")
              
        #acquisition
        print("  run acquisition")
        camSpectro = connectCam(config)
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
    print("Plate Solving")
    fenteXpix=config["centerX"]
    fenteYpix=config["centerY"]
    scaleArcPerPixelFinder=((config["camera"]["pixelSize"]*0.001*config["camera"]["binning"])/config["FocalLength"]) /6.28 * 360 * 60 *60
    print(f"  Calculated Scale is {scaleArcPerPixelFinder:0.2f} ArcSecond per pixel")
    
    
    try:
        w=solveAstro(fileNameAstro,scaleArcPerPixelFinder)
        wx, wy = w.wcs_pix2world(fenteXpix, fenteYpix,1)
    except:
        print("error during plate solving...")
        abort(500,description='plate solving')
        return { 'error':'error' }

    ### Store & Display Result
    print("  fente X=",fenteXpix," ,Y=",fenteYpix)
    print('  RA={0}deg  DEC={1}deg '.format(wx, wy))

    pi = 3.141592653589793
    result= { "protoVersion":"1.00", "coord": {"RA": wx/180.0*pi, "DEC":wy/180.0*pi , "unit":"RADIAN"}}

    return result


############ main ###############
@app.route('/api/finder/calib', methods=['GET'])
def calib_finder():
    global config
    return jsonify(doFinderCalib(config))

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


        
        
        app.run(host='0.0.0.0',port=5000,debug=True)


