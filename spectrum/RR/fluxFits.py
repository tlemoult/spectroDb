import astropy.io.fits as fits
import click
import os
from scipy import ndimage
from operator import itemgetter, attrgetter
import numpy as np
import matplotlib.pyplot as plt

@click.command()
@click.argument('path' )


def stat(path):

    dirs = os.listdir( path )
    dirs.sort()
    resultLst = []
    for f in dirs:

        if not "OBJECT" in f:
            continue
        filePath = path+'/'+f
        hdulist = fits.open(filePath)
        header = hdulist[0].header
        dateObs = header['DATE-OBS']

        img=ndimage.median_filter(hdulist[0].data,5)
        maxFlux = np.max(img)
        minFlux = np.min(img)

        print(f"file= {f} Min: {minFlux}   Max: {maxFlux}")
    #    print('Mean:', np.mean(img))
    #    print('Stdev:', np.std(img))

        resultLst.append({'filePath':filePath , 'dateObs':dateObs , 'flux':maxFlux-minFlux})

    resultSort = sorted(resultLst , key=itemgetter('dateObs'))

    flux=[r['flux'] for r in resultSort]
    print(f"result: {flux}")

    fig, ax = plt.subplots()
    ax.plot(flux)
    ax.set(xlabel='expusure' , ylabel='Flux', title=path)
    ax.grid()
    ax.set_ylim(bottom=0)
    plt.show()




if __name__ == '__main__':
    stat()
