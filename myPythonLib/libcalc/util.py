from astropy import units as u
from astropy.coordinates import SkyCoord,FK5,AltAz,EarthLocation
from astropy.time import Time
from astropy.utils.iers import Conf as astropyConf
import astropy.io.fits
import subprocess,os,sys,logging

def getEarthLocation(config):
    obsSite=config["obsSite"]
    obsLat=obsSite['latDeg']*u.deg+obsSite['latMin']*u.arcmin+obsSite['latSec']*u.arcsec
    obsLon=obsSite['lonDeg']*u.deg+obsSite['lonMin']*u.arcmin+obsSite['lonSec']*u.arcsec
    return EarthLocation(lat=obsLat,lon=obsLon,height=obsSite['altitude']*u.m)

def getCoordFromName(name):
    c = SkyCoord.from_name(name)
    #print(f"getCoordFromName  name = {name} :\n      {c.ra.hms}  {c.dec.dms}")
    return c

def convJ2000toJNowRefracted(skyCoords,obsSite,pressure=101700*u.pascal,temperature=5*u.Celsius):
    c = skyCoords
    t = Time.now()
    #print(f"Enter convJ2000toJNowRefracted()")
    #print(f"SkyCoords equinox J2000: {c}\n     {c.ra.hms}  {c.dec.dms}")
    
    cJNow = c.transform_to(FK5(equinox=t))
    #print(f"SkyCoords equinox Now:   {cJNow}\n     {cJNow.ra.hms}  {cJNow.dec.dms}")

    cAltAz = c.transform_to(AltAz(obstime=t,location=obsSite))
    #print(f"SkyCoords AltAz: {cAltAz}\n")

    cAltAzRefrac = c.transform_to(AltAz(obstime=t,location=obsSite,pressure=pressure,temperature=temperature,relative_humidity=0.8,obswl=0.65*u.micron))
    #print(f"SkyCoords cAltAzRefrac: {cAltAzRefrac}\n")
    cAltAzRefracTric = AltAz(obstime=t,location=obsSite,alt=cAltAzRefrac.alt,az=cAltAzRefrac.az)
    cJNowRefractedTric = cAltAzRefracTric.transform_to(FK5(equinox=t))
    #print(f"Skycoods cJNowRefacted = {cJNowRefractedTric}\n     {cJNowRefractedTric.ra.hms}  {cJNowRefractedTric.dec.dms}")
    #print(f"  Refraction delta is {abs(cAltAz.alt-cAltAzRefrac.alt).value*60:.1f} arcminutes")
    return cJNowRefractedTric

def scaleImage(pathFilenameSrc,pathFilenameDst,ratio):
    from skimage.transform import resize
    from scipy import ndimage
    from astropy.io import fits

    logger = logging.getLogger('PyQtIndi.IndiClient')
    logger.info(f"scaleImage: resize the source image {pathFilenameSrc} ratio = {ratio}")
    hdulist = fits.open(pathFilenameSrc)

    img=hdulist[0].data
    orgShape = img.shape
    logger.info(f"scaleImage: source image shape = {img.shape}")
    res= resize(img,(orgShape[0],orgShape[1]*ratio))
    logger.info(f"scaleImage: dest image shape = {res.shape}")

    hdu = fits.PrimaryHDU(res)
    hdu.writeto(pathFilenameDst,overwrite=True)

def solveAstro(filename,camera):

    logger = logging.getLogger('PyQtIndi.IndiClient')
    logger.info(f"myLib.util.soveAstro: Plate Solving  file={filename}")
    fenteXpix=camera["centerX"]*camera["pixelSizeX"]/camera["pixelSizeY"]
    fenteYpix=camera["centerY"]
    scaleArcPerPixelFinder=((camera["pixelSizeY"]*0.001*camera["binning"]["X"])/camera["FocalLength"]) /6.28 * 360 * 60 *60
    logger.info(f"  Calculated Scale is {scaleArcPerPixelFinder:0.2f} ArcSecond per pixel")
    logger.info(f"  Optical axis X={fenteXpix} Y={fenteYpix}")

    name, extension = os.path.splitext(filename)
    scale_low = str(scaleArcPerPixelFinder*80.0/100.0)
    scale_high = str(scaleArcPerPixelFinder*120.0/100.0)
    head, tail = os.path.split(filename)
    #solve-field --downsample 2 --tweak-order 2  --overwrite finderAutoSolver-Astro.fits
    with open(head+'/outputAstrometry.txt', "w") as outfile:
        subprocess.call(
            ["/usr/bin/solve-field",
            "--cpulimit","25",
            "--downsample", "4", "--tweak-order", "2", "--scale-units", "arcsecperpix", 
            "--scale-low", scale_low, "--scale-high", scale_high, "--no-plots",
            "--overwrite", filename],
            stdout=outfile
            )
    if os.path.isfile(name+'.solved'):
        logger.info("succes resolution astrometrique, get wcs data")
        wcs = astropy.wcs.WCS(astropy.io.fits.open(name+'.wcs')[0].header)

        try:
            os.remove(name+'-indx.xyls')
            os.remove(name+'.axy')
            os.remove(name+'.corr')
            os.remove(name+'.match')
            os.remove(name+'.new')
            os.remove(name+'.rdls')
            os.remove(name+'.solved')
            #os.remove(name+'.wcs')
        except:
            logger.info("    Some file was not here.")


        ### Store & Display Result
        logger.info("  fente X=",fenteXpix," ,Y=",fenteYpix)
        wx, wy = wcs.wcs_pix2world(fenteXpix, fenteYpix,1)
        logger.info('  RA={0}deg  DEC={1}deg '.format(wx, wy))
        coordsJ2000  = SkyCoord(wx,wy,frame = 'icrs',unit='deg')
        coordsJ2000str = coordsJ2000.to_string('hmsdms')
        raStr, decStr = coordsJ2000str.split(' ')
        logger.info(f"  J2000 coords RA={raStr}  DEC={decStr}")

        return {"wcs":wcs,  "raStr":raStr , "decStr":decStr , "coordsJ2000":coordsJ2000 , "wx":wx , "wy":wy }

    else:
        logger.error("echec resolution astrometrique")
        return None

if __name__ == '__main__':
    print("Demo of util lib")
    astropyConf.auto_download=False
    obsSiteChelles = EarthLocation(lat=48*u.deg+52*u.arcmin+49*u.arcsec,lon=2*u.deg+34*u.arcmin+55*u.arcsec,height=40*u.m)

    convJ2000toJNowRefracted(getCoordFromName('M33'),obsSiteChelles)

