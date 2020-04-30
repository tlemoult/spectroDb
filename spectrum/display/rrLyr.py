from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
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

def plot(path,filename,save=True):

    flux,waveLenght,header = loadSpc(path+'/'+fileName)

    (fig1,axes) = plt.subplots(2,1)

    fig1.set_size_inches(16, 10)
    fig1.suptitle(f"{header['OBJNAME']}, {header['EXPTIME2']}, dateObs(UTC)={header['DATE-OBS']},\n\n {fileName}")

    axes[0].set_title('global data')
    axes[0].plot(waveLenght,flux,'r-')
    axes[0].set_ylim(bottom=0)


    axes[1].set_title('zoom on Ha')
    axes[1].plot(waveLenght,flux,'r-')

    axes[1].set_ylim(bottom=0)
    axes[1].set_xlim(6540,6585)

    if save:
        plt.savefig('plot/plot'+header['DATE-OBS'].replace(':','-')+'.png')
    else:
        plt.show()
    
    plt.close()



#fileName="RRlyr_RRLyr_20200415_153_600_TLE_34.fits"

path="K:/spcWork/RRlyr"
filesName=os.listdir(path)
i=1
for fileName in filesName:
    print(f"{i}/{len(filesName)} file:{fileName}  ")
    plot(path,fileName)
    i=i+1



