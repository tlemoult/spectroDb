import sys,os
import urllib,glob
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
	
print "Script de Nettoyage des dossiers de travail ISIS"

BasePath=sys.path[0]
dbSourcePath=BasePath
PathWeb=BasePath

dirList= os.listdir(dbSourcePath)
dirList=sorted(dirList)

for path in listdirectory(BasePath):
	file=os.path.basename(path)
	if (file.startswith('blaze_') or file.startswith('calib_') or file.startswith('flat_') or file.startswith('#') or (file.endswith('.dat') and not file.startswith('reponse')) or (file.startswith('@') and not file.startswith('@pro')) ):
		print('remove:'+path)
		os.remove(path)
	
