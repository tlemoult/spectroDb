import sys,os
from os import walk
import urllib,glob
import astropy.io.fits as fits
from astropy.time import Time
import zipfile

def explodeFits(pathSrc,pathDst,filenameOrg):
	print("explodeFits src=%s dst=%s filename=%s"%(pathSrc,pathDst,filenameOrg))
	files=[]  # liste des fichiers de sortie
	newBaseName=''
	hdulistOrg = fits.open(pathSrc+'/'+filenameOrg)
	if len(hdulistOrg)<2:  # pas de multiplan, rien a exploser
		return ([],'')

	print("ExplodeFits("+pathSrc+"/"+filenameOrg)	
	headerOrg=hdulistOrg[0].header
	print("OBJ=",headerOrg['OBJNAME']," Date Obs=",headerOrg['DATE-OBS'])
	print("order: ")
	# determine if level is P_1C_ or P_1B
	if 'P_1C_' in ';'.join([ hdu.name for hdu in hdulistOrg]):
		level='P_1C_'
	else:
		level='P_1B_'
	
	for hdu in hdulistOrg:
		if hdu.name.startswith(level):
			order=hdu.name.split(level)[1]

			# create PRIMARY plan of new fits with data
			myHdu=fits.PrimaryHDU(hdu.data)

			# fill header of new plan, with keyword from 
			for key in ['BITPIX','NAXIS','NAXIS1','CRPIX1','CRVAL1','CDELT1','CTYPE1','CUNIT1']:
				myHdu.header[key]=hdu.header[key]
			for key in ['DATE-OBS','DATE-END','MJD-OBS','DATE','SITENAME','ORIGIN','SITELAT','SITELONG','INSTRUME','OBJNAME','OBSERVER','CONFNAME','TELESCOP','DETNAM','ITRP','SWCREATE','BSS_COSM','BINX','BINY']:
				myHdu.header[key]=headerOrg[key]

			myHdu.header['BSS_INST']=headerOrg['CONFNAME']
			myHdu.header['BSS_SITE']=headerOrg['SITENAME']
			myHdu.header['BSS_ITRP']=headerOrg['ITRP']
			myHdu.header['BSS_TELL']='None'
			myHdu.header['BSS_NORM']='None'
			myHdu.header['EXPTIME']=headerOrg['EXPOSURE']
			myHdu.header['EXPTIME2']=str(headerOrg['EXPOSURE'])+'s'
			myHdu.header['VERSION']=headerOrg['SWCREATE']

			t1=Time(myHdu.header['DATE-OBS'],format='isot', scale='utc')
			t1.format = 'jd'
	#		print('DATE-OBS=',t1)
			myHdu.header['JD-OBS']="%.5f"%float(str(t1))

			t2=Time(myHdu.header['DATE-END'],format='isot', scale='utc')
			t2.format = 'jd'
	#		print('DATE-END=',t2)
			myHdu.header['JD-MID']="%.5f"%((float(str(t1))+float(str(t2)))/2)

			dateISIS=headerOrg['DATE-OBS'][:10].replace('-','')+'_'+(("%.3f")%headerOrg['MJD-OBS']).split('.')[1]
			newBaseName='_'+headerOrg['OBJNAME'].replace(' ','').replace('*','s')+'_'+dateISIS+'_'+headerOrg['OBSERVER'].replace(' ','_')+'_'

			if order!='FULL':
				myHdu.header['BSS_ORD']=newBaseName 	
			
			# create new fits package
			myHduList= fits.HDUList([myHdu])
			filename=newBaseName+order+'.fits'
			try:

				myHduList.writeto(pathDst+'/'+filename)

				files.append(filename)

			except:
				print(".")

			print(" ",order)

	hdulistOrg.close()
	return (files,newBaseName)

