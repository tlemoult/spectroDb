import sys,os,datetime
from os import walk
from os import listdir
from os.path import isfile, join

import urllib.request, urllib.parse, urllib.error,glob
import astropy.io.fits as fits
from astropy.time import Time

import lib.dbSpectro as dbSpectro
import lib.explodeFits as expFits
import json

import hashlib
import xmltodict
import tempfile
import zipfile
import shutil
import logging


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
	for spectroType in list(xmlDict.keys()):   # find dateObs from first RAW file
		fileNameImg=xmlDict[spectroType]['GenericName']+'1.fits'
		#print "fileNameImg",fileNameImg 
		s=filename.split('_')
		try:
			hdu=fits.open(path+'/'+fileNameImg)
			header=hdu[0].header
			ret['dateObs']=header['DATE-OBS'][:19]
		except:
			print("can't open Image file: "+fileNameImg)
			try:
				rootfileName='_'+s[1]+'_'+s[2]+'_'+s[3]+'_'
				print("looking for rootfileName="+rootfileName)
				fileNameSpec = [f for f in listdir(path) if isfile(join(path, f)) and f.startswith(rootfileName) and f.endswith('.fits')][0]
				hdu=fits.open(path+'/'+fileNameSpec)
				header=hdu[0].header
				ret['dateObs']=header['DATE-OBS'][:19]
			except:
				print("can't open Image file: so, can't find obstime for "+filename)

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

## TODO   corriger le nom de l o'bjet a partir de ce que l'on en base de donnee.
def getMetaDataFiles(srcPath,filenames,tmpPath):

	print(("getMetaDataFiles: /n  srcPath = "+srcPath))
	print(("  filenames = "+str(filenames)))

	if srcPath.endswith('/calib') or srcPath.endswith('\calib'):
		return calibProcess(srcPath,tmpPath)

	# ce n'est pas un dossier de calib ISIS, on regarde
	print("****** Enter Directory "+srcPath+"  **********")
	metasReturn={}
	responseFound=False
	for filename in filenames:
		ret={'phase':'PROCESS'}
		ret['sourcePath']=srcPath
		ret['sourceFilename']=filename
		ret['destinationFilename']=filename  # default value, could be redefined		
		ret['md5sum']=calcMd5sum(srcPath,filename)

		if filename.endswith('.xml') and filename.startswith('_'):  # probablement un fichier de conf isis
			metasReturn[filename]=parseXmlISIS(srcPath,filename,ret)
			#rint metasReturn[filename]
			if 'eShel' in list(metasReturn[filename].keys()):   # c est un spectro eShel, la reponse na pas besoin d etre trouve,  elle est le dossier calib
				responseFound=True
			else:
				fileResponse=""  # ce n est pas un xml type eShel, on regarde quelle est la reponse instrumentale
				for fr in filenames:
					if fr.startswith(metasReturn[filename]['Response']+'.') and (fr.endswith('.fits') or fr.endswith('.fit') or fr.endswith('.dat')):
						fileResponse=fr
				if fileResponse!="":   # we found the response file.
					responseFound=True
					r={'phase':'PROCESS'}
					r['sourcePath']=srcPath
					r['sourceFilename']=fileResponse
					r['destinationFilename']=fileResponse
					r['md5sum']=calcMd5sum(srcPath,fileResponse)
					r['dateObs']=metasReturn[filename]['dateObs'] # recupere dateObs definis dans XML pour la reponse
					r['fileType']='REPONSE'
					key=filename+'->'+fileResponse
					metasReturn[key]=r

		if filename.endswith('.log') and filename.startswith('_'):  # probablement un fichier de log isis
			metasReturn[filename]=parseLogFileISIS(srcPath,filename,ret)
		
		if (filename.endswith('.fits') or filename.endswith('.fit')):  # fichier fits
			hdu=fits.open(srcPath+'/'+filename)
			header=hdu[0].header
			ret['naxis1']=header['NAXIS1']

			if 'DATE-OBS' in list(header.keys()):
				if header['DATE-OBS']!="":
					ret['dateObs']=header['DATE-OBS']
				else:
					ret['dateObs']="unknow"
			else:
				ret['dateObs']="unknow"
				#ret['dateObs2']=Time(header['DATE-OBS'],format='isot', scale='utc')
			if 'EXPTIME' in list(header.keys()):
				ret['expTime']=header['EXPTIME']
			elif 'EXPOSURE' in list(header.keys()): 		
				ret['expTime']=header['EXPOSURE']

			if 'OBJNAME' in list(header.keys()):			ret['objName']=header['OBJNAME']
			if 'DETNAM' in list(header.keys()): 			ret['detector']=header['DETNAM']
			if 'CCD-TEMP' in list(header.keys()):			ret['tempCCD']=header['CCD-TEMP']
			if 'BIN1' in list(header.keys()):    			ret['binning']=str(header['BIN1'])+'x'+str(header['BIN2'])
			if 'BINX' in list(header.keys()):    			ret['binning']=str(header['BINX'])+'x'+str(header['BINY'])
							
			if len(hdu)>1:   # FITS multiplan
				ret['fileType']="MULTIPLAN"
				metasReturn[filename]=ret
				(newFiles,newBaseName)=expFits.explodeFits(srcPath,tmpPath,filename)
				#print newFiles
				metasReturn.update(getMetaDataFiles(tmpPath,newFiles,tmpPath))

			if header['NAXIS']==1 and 'CRVAL1' in list(header.keys()):   # SPECTRUM
				ret['fileType']="1DSPECTRUM"
				ret['lStart']=header['CRVAL1']
				ret['lStop']=header['CRVAL1']+(header['NAXIS1']-1)*header['CDELT1']
				sf=ret['sourceFilename'].split('.fit')[0]  # short access on filename without extension

				if sf.startswith('@pro'): # partial spectrum from ISIS serie  @pro
					p=sf[4:]  # after  @pro
					if p.isdigit():  # simple spectrum serie
						ret['order']='1'
					elif p[2]=='-' and p.split('-')[0].isdigit() and p.split('-')[1].isdigit():   # is it a echelle spectrum ?
						ret['order']=sf[4:6]
						ret['BSS_ORD']='@pro'
					else:
						continue  # ignore file with @pro but bad format
				elif 'BSS_ORD' in list(header.keys()): # echelle spectrum
					ret['BSS_ORD']=header['BSS_ORD']
					ret['order']=sf.split(ret['BSS_ORD'])[1]
				elif sf.endswith('_full'):   # merged spectrum
					ret['BSS_ORD']=sf.split('full')[0]
					ret['order']='FULL'
				elif sf.endswith('_FULL'):   # merged spectrum
					ret['BSS_ORD']=sf.split('FULL')[0]
					ret['order']='FULL'
				elif sf.startswith('_'):
					ret['order']='1'
				else:
					continue
				# ici on a bien un spectre valide
				ret=defineTargetNameSpectrumFile(ret)
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
		if filename in list(metasReturn.keys()):
			meta=metasReturn[filename]
			if 'BSS_ORD' in list(meta.keys()) and meta['BSS_ORD']!="":
				orderLog=" Eshel order="+meta['order']
			else:
				orderLog=""
			print("FoundFileType("+filename+")-> "+ metasReturn[filename]['fileType'] + "   DateObs=" + metasReturn[filename]['dateObs']+orderLog)


	if not responseFound:
		# try to find a response file
		print("Try to find a response")
		for filename in filenames:
			if 'reponse' in filename or 'response' in filename:
				fileResponse=filename
				responseFound=True
				break

		if responseFound:
			print("ReponseFilenmae=",fileResponse)
			# build a list of targets
			targets={}
			for filename in metasReturn: 
				meta=metasReturn[filename]
				if meta['fileType']=='1DSPECTRUM':
					if not meta['objName']=='':
						targets[meta['objName']]=meta['dateObs']

			print("Target List=",targets)
			r={'phase':'PROCESS'}
			r['sourcePath']=srcPath
			r['sourceFilename']=fileResponse
			r['destinationFilename']=fileResponse
			r['md5sum']=calcMd5sum(srcPath,fileResponse)
			r['fileType']='REPONSE'

			# for each object, we add a the response file
			for objName in targets:
				newR=r
				newR['dateObs']=targets[objName]
				synthName=objName+'_gess_reponse'
				metasReturn[synthName]=newR
				print("synthName",synthName)
				print(newR)

	return metasReturn



def setDstPath(metas,db):

	

	noDirFound=[]

	for f in metas:
		print("found destination of file "+f,"--->", end=' ')

		#print "f=",f					
		dateObs=metas[f]['dateObs']
		if dateObs=="unknow":
			print("DateObs unknow")
			continue

		r=findPathFromObsDate(metas[f]['dateObs'],db)

		if 'path' in list(r.keys()):
			goodR=r  # pour recylage... dans le block en dessous
			print(r['path']+" obsId="+str(r['obsId']))
			metas[f]['destinationPath']=r['path']+'/wrk'
			metas[f]['obsId']=r['obsId']
		else:
			print("Warning path not found")
			noDirFound.append(f)

	if len(noDirFound)!=0: 
		print("*** No Dir Found **", noDirFound)
		for f in noDirFound:
			if f.startswith('check2.fit'):
				for m in metas:
					if metas[m]['fileType']=='LOGFILEISIS':
						dateObs=metas[f]['dateObs']
						metas[m]['dateObs']=dateObs
						print("LOGFILEISIS Found")
				r=findPathFromObsDate(dateObs,db)
				if 'path' not in list(r.keys()):
					r=goodR  # recyclage d'un valeur dans le dossier
				
				print("check2.fits file use DateObs= "+dateObs+" from LogFile="+m+ "  dstPath --->"+r['path']+" ObsId="+str(r['obsId']))

				metas[f]['destinationPath']=r['path']+'/wrk'
				metas[f]['obsId']=r['obsId']
			else:
				print("unknow path")

	return metas

def findPathFromObsDate(dateObs,db):
	global globPathCache  # cache pour les path et ObsId connus en fonction de dateObs
	if not dateObs in list(globPathCache.keys()):  # on ne connais pas de repertoire pour cette date
		r=dbSpectro.getDirectory_from_STRdate(db,dateObs)
		if 'path' in list(r.keys()):
			globPathCache[dateObs]=r
		else:
			path=""
	else:
		r=globPathCache[dateObs]  # path et obsID deja connus pour cette date d'observation
	return r




def calibProcess(srcPath,tmpPath):
	print("************************************************")
	print("*******C A L I B    P r o c e s s **************")

	metas={}
	print("calibProcess")
	print(("  srcpath", srcPath))
	parentSrc=srcPath.split('/calib')[0]
	print(("  parent Source",parentSrc))

	logFiles = [f for f in listdir(parentSrc) if isfile(join(parentSrc, f)) and f.endswith('.log')]
	calibFiles= [f for f in listdir(srcPath) if isfile(join(srcPath, f))]
	print(("  logFiles",logFiles))
	print(("  calibFiles",calibFiles))
	for f in logFiles:
		metaLog={'sourceFilename':f,'sourcePath':parentSrc}
		metaLog=parseLogFileISIS(parentSrc,f,metaLog)
		print(("  dateObs "+metaLog['dateObs']))
		archiveName='calib.zip'  # metaLog['dateObs'].replace(' ','-').replace(':','-')+
		print((" create archive"+archiveName))
		meta={}
		meta['sourceFilename']=archiveName
		meta['destinationFilename']=archiveName
		meta['sourcePath']=tmpPath
		pythonPath=os.getcwd()
		os.chdir(srcPath)

		fileMd5sum=open(tmpPath+'/md5sum.txt','w')  # store all md5sum
		with zipfile.ZipFile(tmpPath+'/'+archiveName,'w') as myzip:
			for f in calibFiles:
				fileMd5sum.write(calcMd5sum('.',f))
				myzip.write(f)
		fileMd5sum.close()

		os.chdir(pythonPath)  # return to original path
		meta['fileType']='CALIBDIRISIS'
		meta['dateObs']=metaLog['dateObs']			# use logfile
		meta['md5sum']=calcMd5sum(tmpPath,'md5sum.txt')   # md5sum on md5sum

		metas[meta['sourceFilename']]=meta

		print(('  Md5sum = '+str(meta['md5sum'])))
	return metas


def defineTargetNameSpectrumFile(meta):
#	print json.dumps(meta,sort_keys=True, indent=4)
	observer="TLE"
	filename=meta['sourceFilename']
	try:
		hours=int(meta['dateObs'][11:13])
		minutes=int(meta['dateObs'][14:16])
		seconds=int(meta['dateObs'][17:19])
	except:
		print(filename+"-> Cannot rename file, the DateObs is incorrect")
		return meta

	fracDay=str(hours/24.0+minutes/24.0/60.0+seconds/24.0/60.0/60.0)[2:5]

	datestr=meta['dateObs'][:10].replace('-','')

	newBaseName='_'+meta['objName'].replace(' ','')+'_'+datestr+'_'+fracDay+'_'+str(int(round(float(meta['expTime']))))+'_'+observer
	extensionFit=filename.split('.')[-1]

	if 'BSS_ORD' in list(meta.keys()):
		addOrder='_'+meta['order']
		meta['destinationBSS_ORD']=newBaseName+'_'
	else:
		addOrder=''
	meta['destinationFilename']=newBaseName+addOrder+'.'+extensionFit

	return meta

def createDir(dirpath):
    print("test create Dir")
    print(("dirpath="+dirpath))

    if dirpath[1]==':':
        pwd=dirpath[0:3]
        dirpath=dirpath[3:]
    elif dirpath[0]=='/':
        pwd="/"
        dirpath=dirpath[1:]
    else:
        pwd=""

    print(("new dirPath="+dirpath))
    print(("pwd = "+pwd))
    pathList=dirpath.split('/')
    print(("pathList = ",pathList))

    for path in pathList:
        pwd+=path+'/'
        print(("seq pwd: "+pwd))

        try:
            os.stat(pwd)
        except:
			print(("create dir "+pwd))
			os.mkdir(pwd)


def archiveFiles(metas,pathArchive,enableDelete):

	for f in metas:
		meta=metas[f]

		if 'destinationPath' in list(meta.keys()):
			
			if meta['fileType']=='CALIBDIRISIS':
				packExist=dbSpectro.getPathFilename_from_md5sum(db,meta['md5sum'])
				print("packExist=",packExist, "   type(packExist)=",type(packExist))
			else:
				packExist=None

			if packExist!=None:
				# fichier deja trouve,  on modifie le fichier cible
				print("file already exist here"+ packExist[0]+'/'+packExist[1]) 
				meta['destinationPath']=packExist[0]
				meta['destinationFilename']=packExist[1]
			else:
				# nouveau fichier, on le copie dans les dossiers
				dstDir=pathArchive+"/archive"+meta['destinationPath']
				createDir(dstDir)
				shutil.copyfile(meta['sourcePath']+'/'+meta['sourceFilename'],dstDir+'/'+meta['destinationFilename'])

			if dbSpectro.insert_filename_meta(db,meta):
				dbSpectro.update_observation_status(db,meta['obsId'],'REDUCED')
				if enableDelete:
					os.remove(meta['sourcePath']+'/'+meta['sourceFilename'])
			else:
				logException(meta['sourcePath']+meta['sourceFilename'],'errorInsertDb')

		else:
			# can't store the file.., copy file to Exception
			logException(meta['sourcePath']+meta['sourceFilename'],'noDestPathFound')

	return

def logException(msg,reason):
	globalExceptFile.write(str(datetime.datetime.today()).replace(' ','T').replace(':','-')+';'+reason+";"+msg+"\n")

def conformBess(metas,tmpPath):
	for f in metas:
		meta=metas[f]

		if meta['fileType']=='1DSPECTRUM':
			# on ouvre le spectre
			fullSourcePath=meta['sourcePath']+'/'+meta['sourceFilename']
			hdulist = fits.open(fullSourcePath)
			prihdr = hdulist[0].header

			# pas de vitesse Helio
			prihdr['BSS_VHEL']=0

			# arondis de EXPTIME
			prihdr['EXPTIME']=int(round(float(meta['expTime'])))

			# on ne veut pas de DATE-END, pour eviter les conflis de valeur avec EXPTIME
			try:
				del prihdr['DATE-END']
			except KeyError:
				pass

			# on corrige BSS_ORD
			if 'BSS_ORD' in list(meta.keys()):
				prihdr['BSS_ORD']=meta['destinationBSS_ORD']

			# on ecris le fichier corrige
			conformFileName='BessConform_'+metas[f]['sourceFilename']
			hdulist.writeto(tmpPath+'/'+conformFileName)

			# le spectre change de nom et chemin pour apres
			metas[f]['sourceFilename']=conformFileName
			metas[f]['sourcePath']=tmpPath

	return metas

#########
# main  #
#########
print("in-process.py")

if len(sys.argv)==1:  # pas d argument
	print("prend un argument pour laisser la source: repertoire")
	print("ou deux arguments pour effacer la source apres integration:   repertoire delete")
	exit()
elif len(sys.argv)==2:  # un seul argument
	enableDelete=False
elif len(sys.argv)==3 and sys.argv[2]=='delete':
	enableDelete=True
	print("efface les fichiers apres integration")

db=dbSpectro.init_connection()
dbSpectro.setLogLevel(4)

# load configuration
json_text=open("../config/config.json").read()
config=json.loads(json_text)
pathArchive=config['path']['archive']
print(("pathArchive = "+pathArchive))

# open exception file
globalExceptFile=open(pathArchive+'/Except-in-processed/except-'+str(datetime.datetime.today()).replace(' ','T').replace(':','-')+'.log','a')

for (dirpath, dirnames, filenames) in walk(sys.argv[1]):
	dirpath=dirpath.replace("\\","/").replace('//','/')
	print("** Boucle principale **")
	print(("  dirpath = "+str(dirpath)))
	print(("  dirnames = "+str(dirnames)))
	print(("  filenames = "+str(filenames)))
	globPathCache={}  # cache pour les path connus en fonction de dateObs
	tmpPath=tempfile.mkdtemp()
	print(("  temporary dir = "+ tmpPath))
	print("***********************")

	try:
		metas=getMetaDataFiles(dirpath,filenames,tmpPath)
		metas=setDstPath(metas,db)
		print((json.dumps(metas,sort_keys=True, indent=4)))

		# redefinis les nom des spectres
		for f in metas: 
			if metas[f]['fileType']=='1DSPECTRUM': 
				defineTargetNameSpectrumFile(metas[f])

		# rend conforme au Format Bess
		metas=conformBess(metas,tmpPath)

		archiveFiles(metas,pathArchive,enableDelete)
	except:
		logging.exception("Main Loop:")
		logException(dirpath,'mainException'+str(sys.exc_info()[0]))

	print("remove temporary Path=",tmpPath)
	shutil.rmtree(tmpPath)
