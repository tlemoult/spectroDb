import pyfits
import click
from scipy import ndimage
import os
import numpy as np

@click.command()
@click.argument('filename' )

def fits2fits(filename):
    print("------------------")
#    hdulist = pyfits.open(filename,mode="update")
    hdulist = pyfits.open(filename)
    print hdulist.info()
    print "---------------------"
    hdu=hdulist[0]
    header=hdu.header
    print "header['bitpix']=",header['bitpix']
    img=hdu.data
    print "numpy type=",img.dtype

    if 'BSCALE' in header.keys():
        print "--found rescale--"
        print "header['BZERO']=",header['BZERO']
        print "header['BSCALE']=",header['BSCALE']
        bzero=header['BZERO']
        del header['BZERO']
        del header['BSCALE']
    else:
        print "--no scale"
        bzero=0


    print "------ convert to float32 ---"
    newImg=np.array(object=img,dtype=float).astype(np.float32)-bzero
#    print "numpy type=",newImg.dtype
#    print "---------------------"

    hdu.data=newImg
    print "header['bitpix']=",hdu.header['bitpix']
    print hdulist.info()

    (basepath,name)=os.path.split(filename)
    newpath=basepath+'/fix.'+name
    if os.path.exists(newpath):
        os.remove(newpath)
    hdulist.writeto(newpath)

#    hdulist.flush()
    hdulist.close()



if __name__ == '__main__':
    fits2fits()
