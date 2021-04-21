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
    waveLenght = np.linspace(start=header['CRVAL1'],num=header['NAXIS1'],stop=header['CRVAL1']+(header['NAXIS1']-1)*header['CDELT1'])

    hdu.close()

    return flux,waveLenght,header

def saveSpc(fileName,newsHeader,flux):
    hdu = fits.PrimaryHDU(flux)
    hdu.header=newsHeader
#    hdu[0].data=flux
    hdu.writeto(fileName)

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
    axes[1].set_xlim(6540,6541)

    if save:
        plt.savefig('plot/plot'+header['DATE-OBS'].replace(':','-')+'.png')
    else:
        plt.show()
    
    plt.close()

def testDeriv():
    y = [1, 2, 3, 4, 4, 5, 6]
    print(f"y={y}")
    dy = np.diff(y)
    print(f"dy={dy}") 
    d2y = np.diff(dy)
    print(f"d2y={d2y}")


def simplePlot(waveLenght,flux,plotTitle):
    fig, ax = plt.subplots()
    ax.plot(waveLenght,flux)

    ax.set(xlabel='time (s)', ylabel='flux',   title=plotTitle)
    ax.grid()

    plt.show()


def deriv(path,filename,dstPath):

    flux,waveLenght,header = loadSpc(path+'/'+fileName)

    cntEch = np.arange(1, len(waveLenght)+1, 1)

    difFlux = np.diff(flux)
    dif2Flux = abs(np.diff(difFlux))

    waveLenghtDif2 = waveLenght[1:-1]   # derivate twice, we lost 1 elements and last element

    #simplePlot(waveLenght[:-1],difFlux,"1st diff")
    #simplePlot(waveLenghtDif2,absD2Flux,"2nd diff")
    # find zeros seg:

 
    lastF=flux[1]
    lastY=dif2Flux[0]
    lastX=waveLenghtDif2[0]
    slope="increase"

    pixelWave=[]
    pixelFlux=[]

    log = False
    for x,y,f in zip(waveLenghtDif2[1:] , dif2Flux[1:] , flux[2:]):
        if log:
            print(f"dif2({x})={y}")

        if slope == "increase" and lastY > y :
            if log:
                print("start to decrease")
            pixelWave.append(lastX)
            pixelFlux.append(lastF)
            slope = "decrease"
        elif slope == "decrease" and lastY < y:
            if log:
                print("start to increade")
            slope = "increase"

        lastF=f
        lastX=x
        lastY=y

    print(f"Nb pixels found = {len(pixelFlux)}")

    # we add the last point of interpolled data
    pixelWave.append(waveLenght[-1])
    pixelFlux.append(flux[-1])

    #convert wavelenght in pixel number.  Int are more easy to debug..
    pixelWaveInt=[ round((waveLenght - header['CRVAL1']) / header['CDELT1']) for waveLenght in pixelWave]


    #convert point in escalier
    barWaveInt=[]
    lastBarWaveInt=0

    barFlux=[]
    lastBarWaveInt=0

    for posSrc in range(len(pixelWaveInt)):
        
        if posSrc != len(pixelWaveInt)-1:
            endPixelPosInt=(pixelWaveInt[posSrc]+pixelWaveInt[posSrc+1])  # double of average
        else:
            endPixelPosInt=len(waveLenght)*2   # last pos 

        sizePixel=endPixelPosInt-lastBarWaveInt


        if log:
            print(f"endPixelPosInt={endPixelPosInt}")
            #print(f"sizePixel={sizePixel}")
            print(f"lastBarWaveInt={lastBarWaveInt}")
        barWaveInt.extend(list(range(int(lastBarWaveInt),int(endPixelPosInt))))
        barFlux.extend([pixelFlux[posSrc]] * int(sizePixel))

        if log:
            print(f"barWaveInt={barWaveInt}")
            print(f"barFlux={barFlux}")

#        input("Press a key")

        lastBarWaveInt=lastBarWaveInt + sizePixel

    barWave=[header['CRVAL1'] +  header['CDELT1']*0.25 + i * header['CDELT1'] / 2 for i in barWaveInt]


    if log:
        print(f"original  data len = {len(flux)}")
        print(f"pixelized data len = {len(barFlux)}")

    #save data
    # modify header for wavelenght
    header['NAXIS1'] = header['NAXIS1'] * 2
    header['CRVAL1'] = header['CRVAL1'] + header['CDELT1'] * 0.25
    header['CDELT1'] = header['CDELT1'] / 2

    saveSpc(dstPath + '/' + fileName,header,barFlux)

    # plot..
    minWavelenght,maxWavelenght= 6540 , 6542
    minWavelenght,maxWavelenght= 6500 , 6720
    fig, ax = plt.subplots(1,1)

    ax.step(waveLenght,flux,'b')
    ax.plot(pixelWave,pixelFlux,'*r')
    ax.step(barWave,barFlux,'g')
    ax.set_xlim(minWavelenght,maxWavelenght)


    plt.grid()
    plt.show()

def enquete(fileBilin,fileSpline,fileRepixel):
    fluxBilin,waveLenghtBilin,headerBilin = loadSpc(fileBilin)
    fluxSpline,waveLenghtSpline,headerSpline = loadSpc(fileSpline)
    fluxRepixel,waveLengthRepixel,headerRepixel = loadSpc(fileRepixel)
    fig, ax = plt.subplots(1,1)

    ax.step(waveLenghtBilin,fluxBilin)
    ax.step(waveLenghtSpline,fluxSpline)
    ax.step(waveLengthRepixel,fluxRepixel)
    fig.suptitle("Compare plot\n"+fileBilin+" ->>> Blue\n vs "+fileSpline+" ->>> Orange\n and Repixel Version ->>> Green")
    plt.grid()
    plt.show()



"""
********************
*   main code here *
********************
"""

enquete("./_RRLyr_20200726_976_600_TLE_34_bilin.fits","./_RRLyr_20200726_976_600_TLE_34_spline.fits","./_RRLyr_20200726_976_600_TLE_34_bilin_repixel.fits")
exit()

srcPath="./data"
dstPath="./dataPixel"
filesName=os.listdir(srcPath)
i=1
for fileName in filesName:
    print(f"{i}/{len(filesName)} file:{fileName}  ")
    #plot(srcPath,fileName,save=False)
    deriv(srcPath,fileName,dstPath)
    i=i+1



