import pyfits
import click
from scipy import ndimage

import numpy as np

@click.command()
@click.argument('filename' )

def stat(filename):
    print ("Filename=",filename)

    hdulist = pyfits.open(filename)
    print hdulist.info()
    img=ndimage.median_filter(hdulist[0].data,3)

    print('Min:', np.min(img))
    print('Max:', np.max(img))
    print('Mean:', np.mean(img))
    print('Stdev:', np.std(img))

if __name__ == '__main__':
    stat()
