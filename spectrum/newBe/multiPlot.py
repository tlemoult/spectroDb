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

def plots(loadPath='.',savePath='.',save=True, offsetStep=1, xmin=False, xmax=False, xCentral=False, xLen=False):

    print(f"loadPath = {loadPath}")
    dirEndName=loadPath.split('/')[-1]
    filesName=os.listdir(loadPath)
    selectFilename=[]

    #select correct fileNames
    for fileName in filesName:
        if fileName.endswith('.fit') or fileName.endswith('.fits'):
            selectFilename.append(loadPath+'/'+fileName)

    selectFilename.sort(reverse=True)

    fluxes, waves, headers = [] , [], []
    for fileName in selectFilename:
        print(f"load file = {fileName}")
        flux,wave,header=loadSpc(fileName)
        fluxes.append(flux)
        waves.append(wave)
        headers.append(header)


    fig = plt.figure(figsize=(4, 4))
    ax=plt.axes()

    ax.grid(which='both')
#    ax.set_ylim(bottom=0,top=offsetStep*len(selectFilename)+3)
    ax.set_ylim(bottom=0,auto=True)
    ax.set_xticks(np.arange(xmin,xmax,1))
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d A'))
    ax.xaxis.set_minor_locator(MultipleLocator(5))

    if xmin!=False:
        ax.set_xlim(xmin,xmax)
    elif xCentral!=False and xLen!=False:
        ax.set_xlim(xCentral-xLen/2,xCentral+xLen/2)

    offset=len(selectFilename)-1
    for flux,wave,header,fileName in zip(fluxes,waves,headers,selectFilename):

        try:
            waveCoorHelio = coorHelioSpeed(wave,header)
        except ValueError:
            waveCoorHelio = wave
            print("************ Warning missing Helio correction *********")

        flux+=offset
        ax.plot(waveCoorHelio,flux,label=header['DATE-OBS'][:10]+" "+header['OBSERVER'])
        offset-=offsetStep


    ax.legend( loc="lower center", bbox_to_anchor=(0.4, -1))
    fig.subplots_adjust(bottom=0.45)

    xmin,xmax,ymin,ymax = plt.axis()

    title=header['OBJNAME']
    ax.set_title(title)


    if save:
        fileNameSave=dirEndName+'plot_'+header['OBJNAME'].replace(' ','_')+'_'
        fileNameSave+=f"{int((xmin+xmax)/2)}A_"
        fileNameSave+=f"{header['DATE-OBS'].replace(':','_')}.png"
        print(f"save '{fileNameSave}' in '{savePath}'")
        plt.savefig(savePath+'/'+fileNameSave)
    else:
        plt.show()
    
    plt.close()


#dataPath = "U:/astro/mes_articles/newBe/2020-aa/data/"
dataPath = "./data/"
savePath="./plot"

dirs = os.listdir(dataPath)
for dir in dirs:
    print(f"source path = {dataPath+dir}")
    plots(loadPath=dataPath+dir,savePath=savePath,save=True,offsetStep=1,xCentral=6562,xLen=50)



