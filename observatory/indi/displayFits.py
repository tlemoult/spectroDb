
import sys
import matplotlib.pyplot as plt
from astropy.io import fits

n=len(sys.argv)
print(f" len(sys.argv[]) = {n}")

if n!=2:
    print("syntaxe:")
    print('    python displayFits.py image.fits')
    exit()


fits_image_filename=sys.argv[1]
print(f"fits_image_filename = {fits_image_filename}")
hdul = fits.open(fits_image_filename)
print(f"hdul.info() = {hdul.info()}")

img = hdul[0].data

plt.imshow(img, cmap=plt.cm.gray, clim=(4000, 12000)) 
plt.show()


