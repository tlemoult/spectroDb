from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import os,sys

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

def plot(path,filename,save=True,zoomWaveLenght=None,zoomTitle=""):

    flux,waveLenght,header = loadSpc(path+'/'+fileName)

    (fig1,axes) = plt.subplots(2,1)

    fig1.set_size_inches(16, 10)
    fig1.suptitle(f"{header['OBJNAME']}, {header['EXPTIME2']}, dateObs(UTC)={header['DATE-OBS']},\n\n {fileName}")

    axes[0].set_title('global data')
    axes[0].plot(waveLenght,flux,'r-')
    axes[0].set_ylim(bottom=0)


    axes[1].set_title('zoom on '+zoomTitle)
    axes[1].plot(waveLenght,flux,'r-')

    if zoomWaveLenght!=None:
        axes[1].set_ylim(top=2.5,bottom=1.9)
        axes[1].set_xlim(zoomWaveLenght[0],zoomWaveLenght[1])

    if save:
        plt.savefig('plot/plot'+header['DATE-OBS'].replace(':','-')+'.png')
    else:
        plt.show()
    
    plt.close()



#fileName="RRlyr_RRLyr_20200415_153_600_TLE_34.fits"

if len(sys.argv) < 2:
    print("nombre d'argument incorrect")
    print("utiliser: ")
    print("   python plot.py path")
    exit(1)

path=sys.argv[1]
filesName=os.listdir(path)
i=1
for fileName in filesName:
    print(f"{i}/{len(filesName)} file:{fileName}  ")
    plot(path,fileName,zoomWaveLenght=[4681,4691],zoomTitle="on 4686A")
    """    plot(path,fileName,zoomWaveLenght=[6540,6585],"on Ha") """
    i=i+1



