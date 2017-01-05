import sys,os
from os import walk
from os import listdir
from os.path import isfile, join

import urllib,glob
import pyfits
from astropy.time import Time

import lib.dbSpectro as dbSpectro
import lib.explodeFits as expFits
import json

import hashlib
import xmltodict
import tempfile
import zipfile


def calcMd5sum(path,filename):
	BLOCKSIZE = 65536
	hasher = hashlib.md5()
	with open(path+'/'+filename, 'rb') as afile:
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
	return hasher.hexdigest()


def parseXmlISIS(path,filename,ret):
	ret['fileType']="CONFISIS"

	with open(path+'/'+filename) as fd:
		xmlDict = xmltodict.parse(fd.read())
	ret.update(xmlDict)

	ret['dateObs']="unknow"
	for spectroType in xmlDict.keys():   # find dateObs from first RAW file
		fileNameImg=xmlDict[spectroType]['GenericName']+'1.fits'
		#print "fileNameImg",fileNameImg 
		s=filename.split('_')
		try:
			hdu=pyfits.open(path+'/'+fileNameImg)
			header=hdu[0].header
			ret['dateObs']=header['DATE-OBS'][:19]
		except:
			print "can't open Image file: "+fileNameImg
			try:
				rootfileName='_'+s[1]+'_'+s[2]+'_'+s[3]+'_'
				fileNameSpec = [f for f in listdir(path) if isfile(join(path, f)) and f.startswith(rootfileName) and f.endswith('.fits')][0]
				hdu=pyfits.open(path+'/'+fileNameSpec)
				header=hdu[0].header
				ret['dateObs']=header['DATE-OBS'][:19]
			except:
				print "can't open Image file: so, can't find obstime for "+filename

		if spectroType!="eShel":
			ret['Response']=xmlDict[spectroType]['ResponseFile']
		return ret

def parseLogFileISIS(path,filename,ret):
	ret['fileType']="LOGFILEISIS"

	f=open(path+'/'+filename,'r')
	date=""
	for l in f:
		if l.startswith("Date de prive de vue"):
			date=l.split('Date de prive de vue :')[1].strip()
			day=date[0:2]
			month=date[3:5]
			year=date[6:10]
			ret['dateObs']=year+"-"+month+"-"+day+date[10:19]
			break

	if date=="":
		ret['dateObs']="unknow"

	f.close()
	return ret


def getMetaDataFiles(srcPath,filenames,tmpPath):
	metasReturn={}
	for filename in filenames:
		ret={'phase':'PROCESS'}
		ret['sourcePath']=srcPath
		ret['filename']=filename
		ret['md5sum']=calcMd5sum(srcPath,filename)

		if filename.endswith('.xml') and filename.startswith('_'):  # probablement un fichier de conf isis
			metasReturn[filename]=parseXmlISIS(srcPath,filename,ret)
			#rint metasReturn[filename]
			fileResponse=metasReturn[filename]['Response']+'.fits'
			r={'phase':'PROCESS'}
			r['sourcePath']=srcPath
			r['filename']=fileResponse
			r['md5sum']=calcMd5sum(srcPath,fileResponse)
			r['dateObs']=metasReturn[filename]['dateObs']
			r['fileType']='REPONSE'
			key=filename+'->'+fileResponse
			metasReturn[key]=r

		if filename.endswith('.log') and filename.startswith('_'):  # probablement un fichier de log isis
			metasReturn[filename]=parseLogFileISIS(srcPath,filename,ret)
		
		if (filename.endswith('.fits') or filename.endswith('.fit')):  # fichier fits
			hdu=pyfits.open(srcPath+'/'+filename)
			header=hdu[0].header
			ret['naxis1']=header['NAXIS1']
			if 'DATE-OBS' in header.keys():
				if header['DATE-OBS']!="":
					ret['dateObs']=header['DATE-OBS']
				else:
					ret['dateObs']="unknow"
			else:
				ret['dateObs']="unknow"
				#ret['dateObs2']=Time(header['DATE-OBS'],format='isot', scale='utc')
			if 'EXPTIME' in header.keys():
				ret['expTime']=header['EXPTIME']
			elif 'EXPOSURE' in header.keys():
				ret['expTime']=header['EXPOSURE']

			if 'OBJNAME' in header.keys():
				ret['objName']=header['OBJNAME']
							
			if len(hdu)>1:   # FITS multiplan
				ret['fileType']="MULTIPLAN"
				metasReturn[filename]=ret
				(newFiles,newBaseName)=expFits.explodeFits(srcPath,tmpPath,filename)
				#print newFiles
				metasReturn.update(getMetaDataFiles(tmpPath,newFiles,tmpPath))

			if header['NAXIS']==1:   # SPECTRUM
				ret['fileType']="1DSPECTRUM"
				ret['lStart']=header['CRVAL1']
				ret['lStop']=header['CRVAL1']+(header['NAXIS1']-1)*header['CDELT1']

				if ret['filename'].startswith('@pro'):  # partial spectrum from ISIS serie
					ret['order']=ret['filename'][4:6]
					ret['BSS_ORD']='@pro'
				elif 'BSS_ORD' in header.keys(): # echelle spectrum
					ret['BSS_ORD']=header['BSS_ORD']
					ret['order']=ret['filename'].split(ret['BSS_ORD'])[1].split('.')[0]
				elif ret['filename'].split('.')[0].endswith('_full') or ret['filename'].split('.')[0].endswith('_FULL'):   # merged spectrum
					ret['BSS_ORD']=ret['filename'].split('full.')[0]
					ret['order']='Merged'
				else:
					ret['BSS_ORD']=''
					ret['order']='1'
				metasReturn[filename]=ret

			if header['NAXIS']==2:
				ret['naxis2']=header['NAXIS2']
				if filename.startswith('_'):
					ret['fileType']="2DSPECTRUM"
					metasReturn[filename]=ret

				if filename.startswith('check2.fit'):
					ret['fileType']="CALIBCHECK"
					metasReturn[filename]=ret

		# if we indentify the file, we print a log
		if filename in metasReturn.keys():
			meta=metasReturn[filename]
			if 'BSS_ORD' in meta.keys() and meta['BSS_ORD']!="":
				orderLog=" Eshel order="+meta['order']
			else:
				orderLog=""
			print "FoundFileType("+filename+")-> "+ metasReturn[filename]['fileType'] + "   DateObs=" + metasReturn[filename]['dateObs']+orderLog

	return metasReturn



def setDstPath(metas,db):
	noDirFound=[]

	for f in metas:
		print "found destination of file "+f,"--->",

		#print "f=",f					
		dateObs=metas[f]['dateObs']
		if dateObs=="unknow":
			print "DateObs unknow"
			continue

		path=findPathFromObsDate(metas[f]['dateObs'],db)

		if path!="":
			print path
			metas[f]['destinationPath']=path
		else:
			print "Warning path not found"
			noDirFound.append(f)

	if len(noDirFound)!=0: 
		print "*** No Dir Found **", noDirFound
		for f in noDirFound:
			if f.startswith('check2.fit'):
				for m in metas:
					if metas[m]['fileType']=='LOGFILEISIS':
						dateObs=metas[f]['dateObs']
						metas[m]['dateObs']=dateObs
				path=findPathFromObsDate(dateObs,db)
				print "check2.fits file use DateObs= "+dateObs+" from LogFile="+m+ "  dstPath --->"+path

				metas[f]['destinationPath']=path
				print path
			else:
				print "unknow path"

	return metas

def findPathFromObsDate(dateObs,db):
	global globPathCache  # cache pour les path connus en fonction de dateObs
	if not dateObs in globPathCache.keys():  # on ne connais pas de repertoire pour cette date
		path=dbSpectro.getDirectory_from_STRdate(db,dateObs)
		if path!="":
			globPathCache[dateObs]=path
		else:
			path=""
	else:
		path=globPathCache[dateObs]  # path deja connus pour cette date d'observation
	return path




def calibProcess(srcPath,tmpPath):
	metas={}
	print "srcpath", srcPath
	parentSrc=srcPath.split('/calib')[0]
#	print "parent Source",parentSrc

	logFiles = [f for f in listdir(parentSrc) if isfile(join(parentSrc, f)) and f.endswith('.log')]
	calibFiles= [f for f in listdir(srcPath) if isfile(join(srcPath, f))]
#	print logFiles
	for f in logFiles:
		metaLog={'filename':f,'sourcePath':parentSrc}
		metaLog=parseLogFileISIS(parentSrc,f,metaLog)
		print "dateObs "+metaLog['dateObs']
		archiveName=metaLog['dateObs'].replace(' ','-').replace(':','-')+'-calib.zip'
		print "create",archiveName
		meta={}
		meta['filename']=archiveName
		meta['sourcePath']=tmpPath
		with zipfile.ZipFile(tmpPath+'/'+archiveName,'w') as myzip:
			for f in calibFiles:
				myzip.write(srcPath+'/'+f)

		meta['fileType']='CALIBDIRISIS'
		meta['dateObs']=metaLog['dateObs']
		meta['Md5']=calcMd5sum(tmpPath,archiveName)

		metas[meta['filename']]=meta

		print 'Md5Sum=',meta['Md5'],""
	return metas



def archiveFiles(metas):
	#si le fichier existe deja (d apres MD5sum, alors on ne le restocke pas ??
	# mais un lien vers le fichier doit exister
	return



#########
# main  #
#########
print "in-process.py"


if len(sys.argv)==1:  # pas d argument
	print "prend un argument: repertoire de travail"
	exit()

db=dbSpectro.init_connection()

tmpPath=tempfile.mkdtemp()
print "temporary dir", 	tmpPath


for (dirpath, dirnames, filenames) in walk(sys.argv[1]):
	globPathCache={}  # cache pour les path connus en fonction de dateObs
	if dirpath.endswith('/calib'):
		print "************************************************"
		print "*******C A L I B    P r o c e s s **************"
		metas=calibProcess(dirpath,tmpPath)
	else:
		print "************************************************"
		print "****** Enter Directory "+dirpath+"  **********"
		metas=getMetaDataFiles(dirpath,filenames,tmpPath)

	print "******** Find directory ********"
	metas=setDstPath(metas,db)
	#print json.dumps(metas,sort_keys=True, indent=4)
	archiveFiles(metas)