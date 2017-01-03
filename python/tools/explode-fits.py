import sys,os
from os import walk
import urllib,glob
import pyfits
from astropy.time import Time
import zipfile

def print_header(header):
	for k in header.keys():
		print k,"=",header[k]




def explodeFits(path,filenameOrg):
	files=[]  # liste des fichiers de sortie
	newBaseName=''
	hdulistOrg = pyfits.open(path+'/'+filenameOrg)
	if len(hdulistOrg)<2:  # pas de multiplan, rien a exploser
		return ([],'')

	print "ExplodeFits("+path+"/"+filenameOrg	
	headerOrg=hdulistOrg[0].header
	#print_header(headerOrg)
	#print hdulistOrg.info()
	print "OBJ=",headerOrg['OBJNAME']," Date Obs=",headerOrg['DATE-OBS']
	print "order: ",
	for hdu in hdulistOrg:
	#	print "****************************** name=",hdu.name,"****************************"
	#	print_header(hdu.header)
		if hdu.name.startswith('P_1C_'):
			order=hdu.name.split('P_1C_')[1]

			# create PRIMARY plan of new fits with data
			myHdu=pyfits.PrimaryHDU(hdu.data)

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
	#		print 'DATE-OBS=',t1
			myHdu.header['JD-OBS']="%.5f"%float(str(t1))

			t2=Time(myHdu.header['DATE-END'],format='isot', scale='utc')
			t2.format = 'jd'
	#		print 'DATE-END=',t2
			myHdu.header['JD-MID']="%.5f"%((float(str(t1))+float(str(t2)))/2)

			dateISIS=headerOrg['DATE-OBS'][:10].replace('-','')+'_'+(("%.3f")%headerOrg['MJD-OBS']).split('.')[1]
			newBaseName='_'+headerOrg['OBJNAME'].replace(' ','').replace('*','s')+'_'+dateISIS+'_'+headerOrg['OBSERVER'].replace(' ','_')+'_'
			myHdu.header['BSS_ORD']=newBaseName
			
			# create new fits package
			myHduList= pyfits.HDUList([myHdu])
			filename=newBaseName+order+'.fits'
			try:
				myHduList.writeto(path+'/'+filename)
				if order!='FULL':
					files.append(filename)

			except:
				print ".",

			print " ",order,

	hdulistOrg.close()
	return (files,newBaseName)

#########
# main  #
#########
print "prend un argument: repertoire de travail"
if len(sys.argv)==1:  # pas d argument
	
	exit()
else:
	for (dirpath, dirnames, filenames) in walk(sys.argv[1]):
		for f in filenames:
			if f.endswith('.fits') or f.endswith('.fit'):

				(files,newBaseName)=explodeFits(dirpath,f)
				if files!=[]:
					with zipfile.ZipFile(dirpath+'/'+newBaseName+'.zip','w') as myzip:
						for f in files:
							myzip.write(dirpath+'/'+f)

