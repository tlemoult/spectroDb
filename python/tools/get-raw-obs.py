import datetime,time,json
from datetime import datetime
import sys,os,shutil
import urllib,glob
import lib.dbSpectro as dbSpectro
import lib.cds as cds #mes modules

print "Robot extrait les fichiers OBJECT, CALIB, TUNGSTEN, LED pour le pipeline Eshell"

json_text=open("../config/config.json").read()
config=json.loads(json_text)

PathBaseSpectro= config['path']['archive']+'/archive'
destPath=config['path']['eShelPipe']+'/raw'

print "dossier source",PathBaseSpectro
print "dossier destination",destPath

if len(sys.argv)<3:
	print "nombre d'argument incorrect"
	print "utiliser: "
	print "   python get-raw-obs.py obsId dstPath"
	exit(1)

db=dbSpectro.init_connection()

if len(sys.argv)==3:
	obsIds=[int(sys.argv[1])]
	destPath = sys.argv[2]

print("ObsIds = ",obsIds,"destPath = ",destPath)

for obsId in obsIds:
	print "observationID=",obsId

	fileList=dbSpectro.getFilesPerObsId(db,obsId,"""'OBJECT','CALIB','TUNGSTEN','LED','NEON','FLAT','JSON'""")
	print "-----------------------"
	print fileList

	for row in fileList:
		print row
		fileSource=PathBaseSpectro+row[0]+'/'+row[2]
		fileDest=destPath+"/"+row[2]
		print "fileSource",fileSource
		print "fileDest",fileDest
		print "-"

		shutil.copy(fileSource,fileDest)
	

print "------------------------"
print "Fin du robot"
db.close()

