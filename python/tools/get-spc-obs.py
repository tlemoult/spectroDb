import datetime
import time
import json
from datetime import datetime
import sys
import os
import shutil
import urllib
import glob
import lib.dbSpectro as dbSpectro
import lib.cds as cds  # mes modules

print "Robot extrait les fichiers spectres traite"

if len(sys.argv) < 3:
    print "nombre d'argument incorrect"
    print "utiliser: "
    print "   python get-spc-obs.py obsId Id dstPath"
    print "   python get-spc-obs.py objectId Id dstPath"
    print "   python get-spc-obs.py objectId Id orderNo No dstPath"
    exit(1)

db = dbSpectro.init_connection()

if len(sys.argv)>5 and sys.argv[3] == 'orderNo':
	orderNo=sys.argv[4]
	destPath = sys.argv[5]
else:
	orderNo= '*'
	destPath = sys.argv[3]

if sys.argv[1] == 'obsId':
    fileList = dbSpectro.getFilesSpcPerObsId(db, int(sys.argv[2]),orderNo)
elif sys.argv[1] == 'objectId':
    fileList = dbSpectro.getFilesSpcPerObjId(db, int(sys.argv[2]),orderNo)
else:
    print "argument " + sys.argv[1] + " incorrect utiliser ObsId ou objectId"
    db.close()
    exit(1)

json_text = open("../config/config.json").read()
config = json.loads(json_text)

PathBaseSpectro = config['path']['archive'] + '/archive'


print "dossier source", PathBaseSpectro
print "dossier destination", destPath

print "-----------------------"

i = 0
for f in fileList:
    i = i + 1
    fileSource = PathBaseSpectro + f[0] + '/' + f[1]
    fileDest = destPath + f[1]
    print "fileSource", fileSource, "-->fileDest", fileDest
    shutil.copy(fileSource, fileDest)
print str(i) + " files extracted"
db.close()
