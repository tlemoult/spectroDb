import astropy.io.fits as fits

f = fits.open('FINDER-1.fits')  # open a FITS file
hdu=f[0]
scidata = f[0].data
print(scidata[1, 4])

print ("info",f.info())
print ("bitpix=",hdu.header['bitpix'])

print ("data type=",hdu.data.dtype.name)
hdu.scale('float32',bzero=0)
print ("data type=",hdu.data.dtype.name)

