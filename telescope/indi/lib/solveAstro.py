import subprocess,os
from astropy.wcs import WCS
import astropy.io.fits


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
        return False

# exemple utilisation
if __name__ == "__main__":
    fenteXpix=240
    fenteYpix=200

    w=solveAstro("./champs/M95-1.fits",2.25)
    wx, wy = w.wcs_pix2world(fenteXpix, fenteYpix,1)
    print("fente X=",fenteXpix," ,Y=",fenteYpix)
    print('RA={0}deg  DEC={1}deg '.format(wx, wy))

