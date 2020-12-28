from astropy.io import fits
import astropy.units as u
from astropy import constants as const
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import os,sys

# my modules here
import libsdb.dbSpectro as dbSpectro
import libsdb.cds as cds

def loadSpc(fileName):

    hdu = fits.open(fileName)
    header=hdu[0].header
    if False:
#        print(f"header= {header}")
        for k in header:
            print(f"{k} = {header[k]} \t\t\t '{header.comments[k]}''")

    
    flux=hdu[0].data
    waveLenght = np.linspace(start=header['CRVAL1'],num=header['NAXIS1'],stop=header['CRVAL1']+header['NAXIS1']*header['CDELT1'])

    hdu.close()

    return flux,waveLenght,header

def coorHelioSpeed(wave,header):
    #heliocentric velocity correction  see https://docs.astropy.org/en/stable/coordinates/velocities.html

    coordsDict = {
        "Chelles": 
            { "lat":48.880211*u.deg ,  "lon":+2.58202222*u.deg , "alt":40*u.m },
        "THO   robin@threehillsobservatory.co.uk":
            {  "lat":54.746111*u.deg,  "lon":-3.24111111*u.deg , "alt":135*u.m },
        "THREE HILLS OBSERVATORY":
            {  "lat":54.746111*u.deg,  "lon":-3.24111111*u.deg , "alt":135*u.m },
        "Castanet":
            {  "lat":43.517222*u.deg,  "lon":+1.50833333*u.deg , "alt":167*u.m },
        "Bellavista Obs. L'Aquila":
            {  "lat":42.334722*u.deg,  "lon":+13.4063888*u.deg , "alt":660*u.m },
        "Bellavista Obs. L":
            {  "lat":42.334722*u.deg,  "lon":+13.4063888*u.deg , "alt":660*u.m },

        "38420 Revel":
            {  "lat":45.276111*u.deg,  "lon":+5.8827777777*u.deg , "alt":840*u.m},
        "Rouen":
            {  "lat": 49.421666*u.deg, "lon":+1.0891666666*u.deg , "alt":10*u.m },
        "Delamere":
            {  "lat": 53.217836*u.deg, "lon":-2.6591314035*u.deg , "alt":100*u.m },
        "St_Saturnin_les_Avignon":
            {  "lat": 43.9575*u.deg,   "lon":4.93083333333*u.deg , "alt":70 *u.m},
        "Observatoire St Maurice":
            {  "lat": 46.37125*u.deg,  "lon":0.49118055555*u.deg , "alt":118* u.m},
        "Giesen (Germany)":
            {  "lat": 52.19921*u.deg,  "lon":9.90343172157*u.deg , "alt":70* u.m}
    }

    bessSite = header['BSS_SITE']
    print(f"""\n****\nbess Site = {bessSite}""")
    try:
        obsCoords = coordsDict[bessSite]
    except:
        print(f"unknow site, please complete coordsDict")
        sys.exc_info()[0]
        raise

    print(f"obsCoords = {obsCoords}")
    obsLocation = EarthLocation.from_geodetic(lat=obsCoords['lat'],lon=obsCoords['lon'], height=obsCoords['alt'])

    #get coords from CDS
    objName = header['OBJNAME']

    print(f"request CDS on objname = {objName}", end=" ")
    cdsInfo=cds.getsimbadMesurement(objName)

    if 'alpha' in list(cdsInfo.keys()):  # objet connus du CDS ?
        print(f" OK,  ra ={cdsInfo['alpha']}, dec = {cdsInfo['delta']}")
        header['RA'] = cdsInfo['alpha']
        header['DEC'] = cdsInfo['delta']
    else:
        print(f"Object Name = {objName} unknown from CDS")
        raise ValueError(f"Object Name = {objName} unknown from CDS")

    sc = SkyCoord(ra=cdsInfo['alpha'],dec=cdsInfo['delta'],frame='icrs',unit=(u.hourangle, u.deg))
    obsTime=Time(header['DATE-OBS'])
    print(f"dateObs ={obsTime}")
    heliocorr = sc.radial_velocity_correction('heliocentric', obstime=obsTime, location=obsLocation).to(u.m/u.s)
    print(f"heliocorr = {heliocorr}")
    header['BSS_VHEL'] = heliocorr.to(u.km/u.s).value

    helioCorrFactor = 1 + (heliocorr / const.c).value
    print(f"helioCorrFactor = {helioCorrFactor}")
    header['CRVAL1'] = header['CRVAL1'] * helioCorrFactor
    header['CDELT1'] = header['CDELT1'] * helioCorrFactor

    return np.linspace(start=header['CRVAL1'],num=header['NAXIS1'],stop=header['CRVAL1']+header['NAXIS1']*header['CDELT1'])

def speedFct(l,l0):
    # convert in km/s,  return    
    return (l-l0)/l0* 299792.458

def waveFct(speed,l0):
    #speed in km/s  
    #return same unit than l0
    return l0*(speed/299792.458+1)

def doppler(header,centralWave):
    print(f"Start speed = {speedFct(header['CRVAL1'],centralWave)}")
    return np.linspace(start = speedFct(header['CRVAL1'],centralWave), num=header['NAXIS1'], stop= speedFct(header['CRVAL1']+header['NAXIS1']*header['CDELT1'],centralWave))

def truncData(flux,waveCoorHelio,header,waveCentral,speedSpan):

    print(f"truncData startValue CRVAL1 = {header['CRVAL1']} , NAXIS1= {header['NAXIS1']} , CDELT1 = {header['CDELT1']} ")

    waveStart = waveFct(-speedSpan,waveCentral)
    waveStop  = waveFct(+speedSpan,waveCentral)
    print(f"waveStart = {waveStart}, waveStop = {waveStop}")

    #trunc data on left
    if header['CRVAL1'] > waveStart:
        nTruncLeft = 0
    else:
        nTruncLeft = int((waveStart - header['CRVAL1'])/header['CDELT1'])
        header['CRVAL1'] = header['CRVAL1'] + nTruncLeft * header['CDELT1']
        header['NAXIS1'] = header['NAXIS1'] - nTruncLeft

    waveTruncLeft = waveCoorHelio[nTruncLeft:]
    fluxTruncLeft = flux[nTruncLeft:]
    print(f"truncData midvalue:  CRVAL1 = {header['CRVAL1']} , NAXIS1= {header['NAXIS1']} , CDELT1 = {header['CDELT1']} ")

    #trunc data on right 
    if header['CRVAL1']+header['NAXIS1']*header['CDELT1'] < waveStop:
        nTruncRight = 0
    else:
        nTruncRight = int((header['CRVAL1']+header['NAXIS1']*header['CDELT1']-waveStop)/header['CDELT1'])
        header['NAXIS1'] = header['NAXIS1'] - nTruncRight

    waveTruncLeftRight = waveTruncLeft[:-nTruncRight]
    fluxTruncLeftRight = fluxTruncLeft[:-nTruncRight]

    print(f"truncData endvalue:  CRVAL1 = {header['CRVAL1']} , NAXIS1= {header['NAXIS1']} , CDELT1 = {header['CDELT1']} ")

    return fluxTruncLeftRight,waveTruncLeftRight,header

def resolution(header):
    dicResol = {
        'LISA':800 , 'C11_LHIRES_2400_ATK314': 15000 , 'LHIRES3 C9 SXVR-H694': 15000,
        'C11 VHIRES_MO ATIK460EX': 48000
     }

    if 'BSS_ITRP' in header.keys():
        resol = header['BSS_ITRP']
    else:
        resol = dicResol[header['BSS_INST']]  

    return resol

def plots(loadPath='.',savePath='.',save=True, waveCentral=6562.8, speedSpan=1000):

    print(f"loadPath = {loadPath}")
    dirEndName=loadPath.split('/')[-1]
    filesName=os.listdir(loadPath)
    selectFilename=[]

    #select correct fileNames
    for fileName in filesName:
        if fileName.endswith('.fit') or fileName.endswith('.fits'):
            selectFilename.append(loadPath+'/'+fileName)
    selectFilename.sort(reverse=False)

    #load fluxes, waves, headers
    fluxes, waves, speeds, headers = [] , [], [], []
    for fileName in selectFilename:
        print(f"load file = {fileName}")
        flux,wave,header=loadSpc(fileName)

        # correct helio speed
        try:
            waveCoorHelio = coorHelioSpeed(wave,header)
        except ValueError:
            waveCoorHelio = wave
            print("************ Warning missing Helio correction *********")

        #Troncate data data
        fluxTruncLeftRight,waveTruncLeftRight,header = truncData(flux,waveCoorHelio,header,waveCentral,speedSpan)

        fluxes.append(fluxTruncLeftRight)
        waves.append(waveTruncLeftRight)
        speeds.append(doppler(header,waveCentral))
        headers.append(header)


    ####################
    # start real plot
    ####################
    n = len(selectFilename)
    print(f"n={n}")
    scaleSize = 3.0
    #sharey=True, sharex=True,
    fig , axs = plt.subplots(1,n,figsize=(n*scaleSize, scaleSize),sharey=True,gridspec_kw={'hspace': 0, 'wspace': 0})
    if n == 1:
        axs = [ axs]

    #find maximum of fluxes,  list of array
    maxFlux=0
    for flux in fluxes:
        maxFlux = max(max(flux),maxFlux)
    
    title = headers[0]['OBJNAME']

#    ax.grid(which='both')
#    ax.set_ylim(bottom=0,top=offsetStep*len(selectFilename)+3)
#    ax.set_ylim(bottom=0,auto=True)
#    ax.set_xticks(np.arange(xmin,xmax,1))
#    ax.xaxis.set_major_locator(MultipleLocator(20))
#    ax.xaxis.set_major_formatter(FormatStrFormatter('%d A'))
#    ax.xaxis.set_minor_locator(MultipleLocator(5))

#    plt.xlabel("Velocity km/s relative to Ha")
#    plt.ylabel("Relative flux")


    for ax,flux,wave,speed,header,fileName in zip(axs,fluxes,waves,speeds,headers,selectFilename):
        ax.set_xlim(-speedSpan,+speedSpan)
        ax.set_xticks([-500,0,500])
        ax.set_ylim(bottom=0,top=maxFlux*1.1)
       
        ax.plot(speed, flux)
        #ax.legend()
        #ax.label_outer()

        ax.text(-900,0.1,"R="+str(resolution(header))+"\n"+header['DATE-OBS'][:10]+" "+header['OBSERVER'])

        #ax.set_xlabel(header['DATE-OBS'][:10]+"\n"+header['OBSERVER'])

    #fig.subplots_adjust(bottom=0.45)
    plt.subplots_adjust(top=0.85,bottom=0.15)
    fig.suptitle(title, fontsize=16)

    if save:
        fileNameSave=dirEndName
        print(f"save '{fileNameSave}' in '{savePath}'")
        plt.savefig(savePath+'/'+fileNameSave+'.png')
        plt.savefig(savePath+'/'+fileNameSave+'.eps')
    else:
        plt.show()
    
    plt.close()


#dataPath = "U:/astro/mes_articles/newBe/2020-aa/data/"
dataPath = "./data/"
savePath="./plot"

dirs = os.listdir(dataPath)
for dir in dirs:
    print(f"source path = {dataPath+dir}")
    plots(loadPath=dataPath+dir,savePath=savePath,save=True, waveCentral=6562.8, speedSpan=1000)



