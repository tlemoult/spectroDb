#!/usr/bin/python
import sys
from astropy.io import fits as pyfits
import numpy as np
import matplotlib.pyplot as plt

def dispESO(filename,xaxis,yaxis):
    print("filename= "+filename)
    hdulist = pyfits.open( filename )
    print(hdulist[1].columns)
    scidata = hdulist[1].data
    header=hdulist[0].header
    print("selected columns")
    print(hdulist[1].columns[xaxis],hdulist[1].columns[yaxis])
    title=header['OBJECT']+'  RA='+str(header['RA'])+' DEC='+str(header['DEC'])
    print(title)

    wave = scidata[0][xaxis]
    flux = scidata[0][yaxis]
    plt.plot(wave, flux)
    plt.title(title)
    plt.xlabel(hdulist[1].columns[xaxis])
    plt.ylabel(hdulist[1].columns[yaxis])

    plt.show()

dispESO("ADP.2016-11-02T09_08_02.791.fits",0,1)
dispESO("ADP.2017-10-27T04_03_47.786.fits",0,4)
dispESO("ADP.2018-11-23T01_04_50.860.fits",0,1)
