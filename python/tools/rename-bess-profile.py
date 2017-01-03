import datetime,time
from datetime import datetime
import sys,os,shutil
import urllib,glob
import pyfits

print "renome les fichiers profil facon ISIS"

if len(sys.argv)<2:
	print "nombre d'argument incorrect"
	print "utiliser: python main-rename-bess-profile.py diretory"
	exit(1)

observer="TLE"
basePath=sys.argv[1]
print "basePath=",basePath

fileList=glob.glob(basePath+'*.fit*')
print fileList

for f in fileList:
	print "********************"
	print "oldName",f

	hdulist = pyfits.open(f)
	prihdr  = hdulist[0].header


	if prihdr['NAXIS']!=1:
		print "Pas de donne a une dimention"
		continue

	t=time.strptime(prihdr['DATE-OBS'][:19],"%Y-%m-%dT%H:%M:%S")
	t=prihdr['DATE-OBS'][11:19].replace(':','')

	hours=int(prihdr['DATE-OBS'][11:13])
	minutes=int(prihdr['DATE-OBS'][14:16])
	seconds=int(prihdr['DATE-OBS'][17:19])
	fracDay=str(hours/24.0+minutes/24.0/60.0+seconds/24.0/60.0/60.0)[2:5]

	datestr=prihdr['DATE-OBS'][:10].replace('-','')

	newbaseName='_'+prihdr['OBJNAME'].replace(' ','')+'_'+datestr+'_'+fracDay+'_'+observer
	
	if 'BSS_ORD' in prihdr.keys():
		print "fichier echelle"
		fordre=f.split(prihdr['BSS_ORD'])[1]
		(ordre,extensionFit)=fordre.split('.')
		addOrder='_'+ordre
		prihdr['BSS_ORD']=newbaseName+'_'
		print "prihdr['BSS_ORD']",prihdr['BSS_ORD']
	else:
		addOrder=''
		extensionFit=f.split('.')[-1]

	print "ordre=",ordre
	print "extensionFit=",extensionFit

	newName=newbaseName+addOrder+'.'+extensionFit
	print "newName",basePath+newName
	

	
	hdulist.writeto(f+'tmp')  # ecris fichier tmps
	hdulist.close(f)		   # ferme initial
	os.remove(f)              # efface initial
	os.rename(f+'tmp',basePath+newName) # renome 

print "------------------------"
print "Fin du robot"

