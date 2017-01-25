import datetime,time,json
from datetime import datetime
import sys,os,shutil
import urllib,glob
import lib.dbSpectro as dbSpectro
import lib.cds as cds #mes modules

print "Robot extrait les fichiers spectres traite"

if len(sys.argv)<3:
	print "nombre d'argument incorrect"
	print "utiliser: "
	print "   python get-spc-obs.py obsId Id dstPath"
	print "   python get-spc-obs.py objectId Id dstPath"
	exit(1)

db=dbSpectro.init_connection()

if sys.argv[1]=='obsId':
	fileList=dbSpectro.getFilesSpcPerObsId(db,int(sys.argv[2]))
elif sys.argv[1]=='objectId':
	fileList=dbSpectro.getFilesSpcPerObjId(db,int(sys.argv[2]))
else:
	print "argument "+sys.argv[1]+" incorrect utiliser ObsId ou objectId"
	db.close()
	exit(1)

json_text=open("../config/config.json").read()
config=json.loads(json_text)

PathBaseSpectro= config['path']['archive']+'/archive'
destPath=sys.argv[3]

print "dossier source",PathBaseSpectro
print "dossier destination",destPath

print "-----------------------"

i=0
for f in fileList:
	i=i+1
	fileSource=PathBaseSpectro+f[0]+'/'+f[1]
	fileDest=destPath+f[1]
	print "fileSource",fileSource, "-->fileDest",fileDest
	shutil.copy(fileSource,fileDest)
print str(i)+" files extracted"
db.close()