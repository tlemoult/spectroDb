import sys,os
import urllib,glob
import pyfits
import fnmatch
import json
import datetime,time

serieID={}  ## identifiant unique des series de fichier pour audela


#transforme la serie aquisition facon ISIS en serie compatible Audela

def clean_coord(coord):
	result=""
	for i in range(len(coord)):
		c=coord[i]
		if (not c.isnumeric()) and c<>'+' and c<>'-' and c<>'.':
			c=' '
		result+=c
	# degage les doubles espaces
	result=' '.join(result.split())
	return result

def load_json(dir):
	path=dir+'/observation.json'
	try:
		print '    try load: "'+path+'" ',
		jsonFile = open(path)
		print "OK"
	except:
		print "    ERROR fichier absent"
		return 0
	
	contentFile = jsonFile.read()
	
	try:
		print "    parse json:",
		jsondata = json.loads(contentFile)
		print " valid"
	except:
		print "    json non valid"
		return 0;

	target=jsondata['target']
	objname=str(target['objname'][0])
	coord=target['coord']
	ra=clean_coord(coord['ra'])
	dec=clean_coord(coord['dec'])

	jsondata['target']['coord']['ra']=ra
	jsondata['target']['coord']['dec']=dec
	
	return jsondata


def listdirectory2(path):  
    a=[]
    l = glob.glob(path+'/*')  
    for i in l:  
        if os.path.isdir(i):
			f=listdirectory(i)
			a.append(f)
    return a

def listdirectory(path):
    fichier=[]
    l = glob.glob(path+'/*')
    for i in l:
        if os.path.isdir(i):
			fichier.extend(listdirectory(i))

	if l==[]:   # dossier vide
		return []

	if fichier==[]:  # on a pas trouve de sous repertoire
		fichier.append(path)
	
    return fichier
	

def def_serie_id(filetype,prihdr):
	global serieID
	if filetype not in serieID.keys():
		print "    new serie Id:"+prihdr['DATE-OBS'],
		print "  filetype="+filetype
		serieID[filetype]=prihdr['DATE-OBS']


def clean_tmp_file(dir):
	l = glob.glob(dir+'/*.fitstmp')
	for path in l:
		os.remove(path)
		
def rastr_to_deg_float(ra):
	rat=ra.split(' ')
	r=float(rat[0])+float(rat[1])/60.0+float(rat[2])
	r=r/24.0*360
	return r

def decstr_to_def_float(dec):
	dect=dec.split(' ')
	if dec[0]=='+':
		sign=+1.0
	else:
		sign=-1.0
	
	if len(dect)==2:  # pas de seconde definies..
		dect.append('00.00')

	d=float(dect[0])+sign*(float(dect[1])/60.0+float(dect[2])/3600.0)
	return d

def get_obj_name_from_filename(path):
	print "Get_obj_name"+path
	objName=""
	
	for ff in os.listdir(path):
		fileName=os.path.basename(ff)
		for rootObj in {'_thor-1.fits','-neonlong-1.fits','-neon-1.fits','_astro2_.fits','_champ.fits'}:
			if fileName.endswith(rootObj):
				baseFileName=fileName.split(rootObj)[0]
				if baseFileName.startswith('REF'):
					objName=baseFileName[4:]
					isRef=True
				elif baseFileName.startswith('Be '): 
					objName=baseFileName[3:]
					isRef=False
				else:
					objName=baseFileName
					isRef=False
				
				if objName.startswith('EMs '):
					print "debug EM*"
					objName='EM* '+objName[4:]
					
				return (objName,baseFileName,isRef)
	print "    Warning no calibration found,  object name unknow or no acquisition"
	return ("","",False)    # on pas trouve d'objet dans le dossier.

def renameFileSeries(directory,fileLST):

	def get_date(a):
		return a['date']
	

	fileLST=sorted(fileLST,key=get_date)
	newFileLST=[]

	d={}
	for f in fileLST:
		fileType=f['typ']
		if fileType=='JSON':
			newFileLST.append(f)
			continue  # on ne s occupe pas des fichiers JSON
		dateObs=f['date']		
		if fileType in d.keys():
			d[fileType].append(f)
		else:
			d[fileType]=[f]

	for t in d.keys():
		#print "Filetype="+t
		index=1
		for f in d[t]:
			oldName=f['filename']
			newName=t+'-'+str(index)+'.fits'
			f['filename']=newName
			#print oldName,'become',newName
			os.rename(directory+'/'+oldName,directory+'/'+newName)
			newFileLST.append(f)
			index+=1

	return newFileLST

def fix_header(objName,baseFileName,isRef,ra,dec,directory,confInstru):
	global serieID
	print "Fix_header objectname="+objName+"  BaseFilename="+baseFileName+" dir="+directory
	serieID={}  ## identifiant unique des series de fichier pour audela
	returnedFileLST=[]

	for ff in os.listdir(directory):
		if fnmatch.fnmatch(ff,'*.fits'):
			path=directory+"/"+ff
			newpath=directory+"/"+ff.replace(' ','_')
			hdulist = pyfits.open(path)
			prihdr  = hdulist[0].header
			
			if 'IMAGETYP' in prihdr.keys():
				filetype=prihdr['IMAGETYP']
			else:
				filetype="none"
				#pour le spectro eShel
				if fnmatch.fnmatch(ff,'Dark*.fits') or fnmatch.fnmatch(ff,'DARK*.fits') or fnmatch.fnmatch(ff,'dark*.fits'):
					filetype="DARK"
				elif fnmatch.fnmatch(ff,'offset*.fits') or fnmatch.fnmatch(ff,'Offset*.fits') or fnmatch.fnmatch(ff,'BIAS-*.fits'):
					filetype="BIAS"
				elif fnmatch.fnmatch(ff,'prnu*.fits') or fnmatch.fnmatch(ff,'PRNU*.fits'):
					filetype="PRNU"
				elif fnmatch.fnmatch(ff,baseFileName+"*_thor-?.fits") or fnmatch.fnmatch(ff,"CALIB-*.fits"):
					filetype="CALIB"
				elif fnmatch.fnmatch(ff,baseFileName+"*_tung-?.fits") or fnmatch.fnmatch(ff,"TUNGSTEN-*.fits"):
					filetype="TUNGSTEN"
				elif fnmatch.fnmatch(ff,baseFileName+"*_led-?.fits") or fnmatch.fnmatch(ff,"*LED-*.fits"):
					filetype="LED"
				# pour le spectro LISA et ALPY
				elif fnmatch.fnmatch(ff,baseFileName+"-neonlong-?.fits") or fnmatch.fnmatch(ff,baseFileName+"-neon-?.fits") or fnmatch.fnmatch(ff,"NEON-?.fits"):
					filetype="NEON"
				elif fnmatch.fnmatch(ff,"flat-*.fits") or fnmatch.fnmatch(ff,"FLAT-*.fits"):
					filetype="FLAT"
				# pour tous les spectros
				elif fnmatch.fnmatch(ff,baseFileName+'-*.fits') or fnmatch.fnmatch(ff,'OBJECT-*.fits'):
					filetype="OBJECT"
				elif fnmatch.fnmatch(ff,"*_astro2_.fits") or fnmatch.fnmatch(ff,"*_champ.fits") or fnmatch.fnmatch(ff,"FIELD-?.fits"):
					filetype="FIELD"

			if filetype!="none":

				# on a reconnus le fichier on le traite
				prihdr['IMAGETYP']=(filetype,'Image type')				
				if filetype!='RESPONSE':
					def_serie_id(filetype,prihdr)
					prihdr['SERIESID']=serieID[filetype]
				print "      "+ff+":filetype->"+filetype
				# add key word in FITS file	
				if 	objName!="":		
					prihdr['OBJNAME']=(objName,'Object observed ')
					
					prihdr['OBJCTRA']=(ra,'Objet Right Ascension J2000')
					prihdr['RA']=(rastr_to_deg_float(ra),'Objet Right Ascension in degre')
					prihdr['OBJCTDEC']=(dec,'Object Declinaison J2000')
					prihdr['DEC']=(decstr_to_def_float(dec),'Object Declinaison J2000 in degre')
					prihdr['EQUINOX']=2000.0

					if isRef:
						prihdr['ISREF']=('TRUE','Is a reference objet')
					else:
						prihdr['ISREF']=('FALSE','Is a reference objet')
					
				prihdr['OBSERVER']=('Thierry Lemoult','Observer name')
				prihdr['SITENAME']=('Chelles','Observatory name')
		
				prihdr['CONFNAME']=(confInstru['configName'],'Configuration name')
				prihdr['BSS_INST']=prihdr['CONFNAME']
			
				prihdr['TELESCOP']=(confInstru['telescop'],'Telescope')
				prihdr['INSTRUME']=(confInstru['spectro'],'spectrographe model')
				if filetype=='FIELD':  # si camera de champ..
					prihdr['DETNAM']=(confInstru['guideDetname'],'Detector')
				else:
					prihdr['DETNAM']=(confInstru['detname'],'Detector')

				prihdr['ITRP']=(confInstru['resol'],'typical spectral resol')

				if 'XBINNING' in prihdr.keys():   # image INDI
					prihdr['BINX']=prihdr['XBINNING']
					prihdr['BINY']=prihdr['YBINNING']
				if 'BINX' in prihdr.keys():
					prihdr['BIN1']=(prihdr['BINX'],'X binning')
					prihdr['BIN2']=(prihdr['BINY'],'Y binning')
				elif 'X1' in prihdr.keys() and 'X2' in prihdr.keys():
					binning=int(round((prihdr['X2']-prihdr['X1'])/float(prihdr['NAXIS1'])))
					prihdr['BIN1']=(binning,'X binning')
					prihdr['BIN2']=prihdr['BIN1']
					prihdr['BINX']=prihdr['BIN1']
					prihdr['BINY']=prihdr['BIN1']
					print "binning calcule=",binning
					
				if (filetype=="BIAS"):
					prihdr['EXPOSURE']=(0,'Exposure time seconds')

				if 'EXPOSURE' not in prihdr.keys():
					prihdr['EXPOSURE']=(0,'Exposure time seconds')

				hdulist.writeto(path+'tmp')
				hdulist.close(path)
				os.remove(path)
				os.rename(path+'tmp',newpath)
				
				if not 'CCD-TEMP' in prihdr.keys():
					prihdr['CCD-TEMP']=0
				
				#info pour stokage dans la base de donne
				returnedFileLST.append({'typ':filetype,'date':datetime.datetime.strptime(prihdr['DATE-OBS'][:19],'%Y-%m-%dT%H:%M:%S'),
										'filename':os.path.basename(newpath),'serieId':serieID[filetype],'detector':prihdr['DETNAM'],
										'ccdTemp':prihdr['CCD-TEMP'],'expTime':str(prihdr['EXPOSURE']),'binning':str(prihdr['BINX'])+'x'+str(prihdr['BINY'])})

	# traite les fichiers json
	for ff in os.listdir(directory):
		if fnmatch.fnmatch(ff,'*.json'):
			returnedFileLST.append({'typ':'JSON','date':datetime.datetime.fromtimestamp(os.path.getmtime(directory+'/'+ff)),
									'filename':ff,'serieId':'None','ccdTemp':None,'binning':None,'detector':None,'expTime':None})
				
	returnedFileLST=renameFileSeries(directory,returnedFileLST)

	if 'OBJECT' in serieID.keys():
		isObservation=True
		dateObs=datetime.datetime.strptime(serieID['OBJECT'][:19],'%Y-%m-%dT%H:%M:%S')
	else:
		isObservation=False
		if serieID.keys()!=[]:
			# on utilise la date de la premiere serie trouvee dans le dictionnaire.
			dateObs=datetime.datetime.strptime(serieID[serieID.keys()[0]][:19],'%Y-%m-%dT%H:%M:%S')
		else:
			dateObs=''  # pas de serieID ... on ne sait pas dater.
	return (isObservation,dateObs,returnedFileLST)
				
