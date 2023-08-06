import libcalc.util as myUtil
import time

def astrometry(loopPoint,cameraGuide,cameraConfig,telescope,J2000Target,obsSite,config):

    fileSerie="getCoordField-"+str(loopPoint)+"-"
    pathAstrometry =  config["path"]["root"] + config["path"]["astrometry"]
    cameraGuide.newAcquSerie(pathAstrometry,fileSerie,1,cameraConfig["expTimeAstrometry"])
    cameraGuide.waitEndAcqSerie()

    filePathAstrometry = pathAstrometry + '/' + fileSerie  + "1.fits"
    astrometryResult = myUtil.solveAstro(filePathAstrometry,cameraConfig)
    if astrometryResult == None:
        print("Echec astrometry")
        return False
        
    print("syncronize telescope")
    telCoords = myUtil.convJ2000toJNowRefracted(astrometryResult["coordsJ2000"],obsSite)
    telescope.syncCoordinates(telCoords)
     
    CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)
    telescope.slewTelescope(CoordTelescopeTarget)
    delayAfterSlew = config["telescope"]["delayAfterSlew"]
    print(f"Wait {delayAfterSlew} seconds after slew...")
    time.sleep(delayAfterSlew)

    return True