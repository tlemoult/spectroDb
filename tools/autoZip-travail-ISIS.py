import sys,os
import urllib.request, urllib.parse, urllib.error,glob
import pyfits
import zipfile
import shutil

def listdirectory(path):  
    fichier=[]  
    l = glob.glob(path+'\\*')  
    for i in l:  
        if os.path.isdir(i): fichier.extend(listdirectory(i))  
        else: fichier.append(i)  
    return fichier

def listdirectory2(path):  
    a=[]
    l = glob.glob(path+'\\*')  
    for i in l:  
        if os.path.isdir(i):
			f=listdirectory(i)
			a.append(f)
    return a
	
print("Script de mise en zip des spectres Traité par ISIS pour publication")

BasePath=sys.path[0]
dbSourcePath=BasePath
PathWeb=BasePath
PathFileTmpDat=BasePath+"@.dat"

dirList= os.listdir(dbSourcePath)
dirList=sorted(dirList)

for dirPath in listdirectory2(BasePath):
	dir=os.path.dirname(dirPath[0])
	print('enter directory: "'+dir+'"')
	spectres=[]
	for path in dirPath:
		file=os.path.basename(path)
		if (file.startswith('_') and file.endswith('.fits') and (not file.endswith('full.fits'))):
			spectres.append(file)
	
	s=spectres[0].split('_')
	starName=s[1]
	obsDay=s[2]
	obsTime=s[3]
	archiveName=starName+"_"+obsDay+"_"+obsTime+"_Thierry_Lemoult.zip"
	print(archiveName)
	os.chdir(dir)
	with zipfile.ZipFile(archiveName,'w') as myzip:
		for file in spectres:
			myzip.write(file)
	shutil.copyfile(dir+'\\'+archiveName,BasePath+'\\'+archiveName)
	
#	print "dir="+os.path.dirname(path)+"  file="+os.path.basename(path)
