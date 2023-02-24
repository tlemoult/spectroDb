import numpy as np
from astropy.io import fits
from scipy import ndimage
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline


def statSpectrum(pathFilename,binnigHeight='auto'):
    #print(f"pathFilename = {pathFilename}")
    
    
    hdulist = fits.open(pathFilename)
    #img=hdulist[0].data
    img=ndimage.median_filter(hdulist[0].data,3)

    
    sumOfRows = np.sum(img, axis=1)

    vertPos = np.argmax(sumOfRows)
    #print(f"spectrum position is {vertPos}")
    x = np.linspace(0,len(sumOfRows)-1,len(sumOfRows))
    xCentre = np.linspace(-vertPos+1,len(sumOfRows)-vertPos,len(sumOfRows))

    minSum = np.min(sumOfRows)
    maxSum = np.max(sumOfRows)

    normer = lambda i: (i -minSum) / (maxSum-minSum)
    sumOfRowsNorm = np.array([normer(i) for i in sumOfRows])

    if binnigHeight == 'auto':
        seuilItrace = 0.5
        stateTrace = 0
        for (p,i) in zip(x,sumOfRowsNorm):
            if i > seuilItrace and stateTrace == 0:
                pInf = int(p)
                stateTrace = 1
            if i < seuilItrace and stateTrace == 1:
                pSup = int(p)
                stateTrace = 2

        #print(f" spectrum position: [{pInf}:{pSup}]")
        factorLarg = 5
        intInf = vertPos - factorLarg * (vertPos - pInf)
        intSup = vertPos + factorLarg * (pSup - vertPos)

    else:
        intInf = vertPos - binnigHeight // 2
        intSup = vertPos + binnigHeight // 2

    #print(f"binnig height = {intSup-intInf}")
    #print(f"spectrum integration position: [{intInf}:{intSup}]")
    imgSpectrum = img[intInf:intSup,:]
    spectrum = np.sum(imgSpectrum, axis=0)

    return { 
        'pos': { 'p': x[intInf:intSup] , 'flux':sumOfRowsNorm[intInf:intSup]},
        'spectrum': spectrum,
        'img': imgSpectrum,
        'mean' : np.mean(imgSpectrum),
        'max' : np.max(imgSpectrum),
        'min' : np.min(imgSpectrum)
        }



if __name__ == '__main__':
    import time
    print("Demo statSpectrum")
    stat = statSpectrum("/mnt/gdrive/astro/base/in/2023-02-12_21-53-05-HD24118/OBJECT-1.fits")

    pos = stat['pos']
    print(f"mean = {stat['mean']}   min = {stat['min']}  max = {stat['max']}")

    print(f"spectrum Integration Y lines: [{pos['p'][0]},{pos['p'][-1]}] ")

    if False:
        # show spectrum position
        plt.plot(pos['p'],pos['flux'])
        plt.title("vertical spectrum position")
        plt.xlabel("Y pixel index")
        plt.ylabel("Normalized flux")
        plt.show()


    plt.ion()
    plt.show()
    fig, (ax1, ax2) = plt.subplots(2,sharex=True)
    fig.suptitle('preview spectrum')
    ax1.set_title("2D image")
    ax1.imshow(stat['img'], cmap=plt.cm.gray) 
    ax2.set_title("binned profil")
    ax2.set_xlabel("pixel X coord")
    ax2.plot(stat['spectrum'])

    plt.draw()
    plt.pause(0.1)
    print("Apres le draw")
    time.sleep(4)
    print("Fin du code")
    time.sleep(4)
    print("Fin du code")

