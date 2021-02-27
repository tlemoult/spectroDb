from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import os

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


def plots(loadPath='.',savePath='.',save=True, offsetStep=0.7, xmin=False, xmax=False, xCentral=False, xLen=False):

    print(f"loadPath = {loadPath}")
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


    plt.figure(figsize=(16, 10))
    ax=plt.axes()

    ax.set_title(f"OBJNAME={header['OBJNAME']}, Exp Time={header['EXPTIME2']}, dateObs(UTC)=[{headers[0]['DATE-OBS']} ... {headers[-1]['DATE-OBS']}]")
    ax.grid(which='both')
    ax.set_ylim(bottom=0,top=offsetStep*len(selectFilename)+3)
    ax.set_xticks(np.arange(xmin,xmax,1))
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d A'))
    ax.xaxis.set_minor_locator(MultipleLocator(1))

    if xmin!=False:
        ax.set_xlim(xmin,xmax)
    elif xCentral!=False and xLen!=False:
        ax.set_xlim(xCentral-xLen/2,xCentral+xLen/2)

    offset=0
    for flux,wave,header,fileName in zip(fluxes,waves,headers,selectFilename):
        flux+=offset
        ax.plot(wave,flux,label=header['DATE-OBS']+' UTC')
        offset+=offsetStep

    ax.legend()

    xmin,xmax,ymin,ymax = plt.axis()

    title=f"OBJNAME={header['OBJNAME']}, Exp Time={header['EXPTIME2']}, \n"
    title+=f"dateObs(UTC)=[{headers[0]['DATE-OBS']} ... {headers[-1]['DATE-OBS']}]\n"
    title+=f"Central Wavelenght = {int((xmin+xmax)/2)}A"
    ax.set_title(title)


    if save:
        fileNameSave='plot_'+header['OBJNAME'].replace(' ','_')+'_'
        fileNameSave+=f"{int((xmin+xmax)/2)}A_"
        fileNameSave+=f"{header['DATE-OBS']}.png"
        print(f"save '{fileNameSave}' in '{savePath}'")
        plt.savefig(savePath+'/'+fileNameSave)
    else:
        plt.show()
    
    plt.close()


rootPathSource="/home/thierry/spectro/RR/2020/ex/"
savePath="/home/thierry/spectro/RR/plot"

plots(loadPath=rootPathSource+"48/corrvrh",savePath=savePath,save=True,offsetStep=0.7,xCentral=4686,xLen=40)
plots(loadPath=rootPathSource+"38/corrvrh",savePath=savePath,save=True,offsetStep=0.7,xCentral=5876,xLen=40)
plots(loadPath=rootPathSource+"34/corrvrh",savePath=savePath,save=True,offsetStep=0.7,xCentral=6678,xLen=40)
plots(loadPath=rootPathSource+"34/corrvrh",savePath=savePath,save=True,offsetStep=0.7,xCentral=6562,xLen=40)




