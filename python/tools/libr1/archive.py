import sys,os,shutil,json

Excep_dir_unknow="unknow_object"
Excep_dir_noFits="no-fits"

#racineArchive="/mnt/gdrive/astro/base"  # linux

def loadConfig():
	print "load config archive: ",
	global racineArchive,pathPipeline
	json_text=open("../config/config.json").read()
	config=json.loads(json_text)
	racineArchive= config['path']['archive']
	pathPipeline= config['path']['eShelPipe']
	print "Path archive archive=",racineArchive
	print "Path Pipeline traitement"

def getFileRaw(fileLST,destDir,obsId):
	pathDst=pathPipeline+'/raw'
	for f in fileLST:
		if f['typ']=='CALIB' or f['typ']=='TUNGSTEN' or f['typ']=='FLAT' or f['typ']=='OBJECT' or f['typ']=='NEON':
			shutil.copyfile(racineArchive+"/archive"+destDir+"/"+f['filename'], pathDst+"/obsId"+str(obsId)+'_'+f['filename'])

def createDir(dateobs):
	dirs=[dateobs[:4],dateobs[5:7],dateobs[8:10],dateobs[11:13]+"h"+dateobs[14:16]+"m"+dateobs[17:19]+"s"]

	current=racineArchive+"/archive"   # chemin absolu
	partDir=''				# chemin relatif
	for d in dirs:
		current=current+"/"+d
		partDir=partDir+"/"+d
		try:
			os.stat(current)
		except:
			os.mkdir(current)
	
	return (current,partDir)
	
def storeDir(sourceDir,dateobs):

	(destDir,partDir)=createDir(dateobs)
	
	destDir+="/raw"
	partDir+="/raw"
	print "archive les fichiers: "+str(sourceDir)+" ---> "+str(destDir)
	
	shutil.move(sourceDir, destDir)
	
	return partDir   # chemin relatif


def moveFiles(sourceDir,dateobs,fileLST):
	(destDir,partDir)=createDir(dateobs)
	os.mkdir(destDir+'/raw')
	destDir+="/raw"
	partDir+="/raw"
	print "archive les fichiers: "+str(sourceDir)+" ---> "+str(destDir)
	for f in fileLST:
		sourcePath=sourceDir+'/'+f['filename']
		destPath=destDir+'/'+f['filename']
		#print 'sourcePath',sourcePath
		#print 'destPath',destPath
		shutil.move(sourcePath,destPath)

	shutil.rmtree(sourceDir)
	return partDir   # chemin relatif
		

	
def storeDir_Excep(sourceDir,exceptName):
	destDir=racineArchive+"/"+exceptName+"/"
	endSource=sourceDir.split('/')[-1]
	print "endSource="+endSource
	
	print "Exception Archive les fichier: "+str(sourceDir)+" ---> "+str(destDir)
	
	try:
		os.stat(destDir+endSource)  # verifie si la destination existe
		print "dest exist"
		shutil.rmtree(destDir+endSource)  # detruis la destination
		shutil.move(sourceDir, destDir)   # copie le dossier
	except:
		shutil.move(sourceDir, destDir)   # deplace le dossier

