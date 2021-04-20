
from flask import Flask, jsonify, abort, make_response
import json,time
import subprocess,os
from astropy.wcs import WCS
import astropy.io.fits

app = Flask(__name__)

def solveAstro(filename,scale):
    print("debut resolution astrometrique ",scale,"arcsec per pixel, file=",filename)
    name, extension = os.path.splitext(filename)
    scale_low = str(scale*80.0/100.0)
    scale_high = str(scale*120.0/100.0)
    subprocess.call(["/usr/bin/solve-field", "--downsample", "2", "--tweak-order", "2", "--scale-units", "arcsecperpix", "--scale-low", scale_low, "--scale-high", scale_high, "--no-plots", "--overwrite", filename])
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

def doFinderSolveAstro(config):
    ### Picture acquisition with Finder Scope
    if config['testWithoutSky']:
        #False image
        fileNameImage=config["imageTest"]
        print(f"Test without sky, use {fileNameImage}",fileNameImage)
        time.sleep(2)
    else:
        #Real image on the sky
        fileNameImage=config["path"]["image"]

        try:
            os.remove(fileNameImage)
        except:
            print("no previous acquisition file {fileNameImage}")
        
        #todo: replace this  C compiled INDI client by pure python with PyIndi lib.
        aquisitionCmdLine =  [config["path"]["camClientExe"],\
						config["camera"]["indiServerAddress"], \
						str(config["camera"]["indiServerPort"]), \
						config["camera"]["name"], \
						str(config["acquisition"]["binning"]), str(config["acquisition"]["binning"]), \
						str(config["acquisition"]["exposureTime"]),\
						fileNameImage]
        subprocess.call(aquisitionCmdLine)
        if not os.path.isfile(fileNameImage):
            abort(500,description='acquisition failed')

    ### Plate Solving
    fenteXpix=config["centerX"]
    fenteYpix=config["centerY"]
    scaleArcPerPixelFinder=config["scale"]
    try:
        w=solveAstro(fileNameImage,scaleArcPerPixelFinder)
        wx, wy = w.wcs_pix2world(fenteXpix, fenteYpix,1)
    except:
        print("error during plate solving...")
        abort(500,description='plate solving')
        return { 'error':'error' }

    ### Store & Display Result
    print("fente X=",fenteXpix," ,Y=",fenteYpix)
    print('RA={0}deg  DEC={1}deg '.format(wx, wy))

    pi = 3.141592653589793
    result= { "protoVersion":"1.00", "coord": {"RA": wx/180.0*pi, "DEC":wy/180.0*pi , "unit":"RADIAN"}}

    return result


############ main ###############
@app.route('/api/finder', methods=['GET'])
def get_finder():
    return jsonify(doFinderSolveAstro(json.loads(open('./configAutoSolver.json').read())))

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)


