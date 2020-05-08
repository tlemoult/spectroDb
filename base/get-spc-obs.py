import datetime
import time
import json
from datetime import datetime
import sys
import os
import shutil
import urllib.request, urllib.parse, urllib.error
import glob
import lib.dbSpectro as dbSpectro
import lib.cds as cds  # mes modules

print("Robot extrait les fichiers spectres traite")

if len(sys.argv) < 3:
    print("nombre d'argument incorrect")
    print("utiliser: ")
    print("   python get-spc-obs.py obsId Id dstPath")
    print("   python get-spc-obs.py objectId Id dstPath")
    print("   python get-spc-obs.py objectId Id orderNo No dstPath")
    print("   python get-spc-obs.py objectId Id orderNo No dstPath date dateStart dateStop")
    print("   python get-spc-obs.py objectId 226 orderNo 34 ./spectrum/RRlyr/34/ date 2019-12-31 2020-12-31")
    exit(1)

db = dbSpectro.init_connection()
print("len(sys.argv)=" , len(sys.argv))
if len(sys.argv)>8 and sys.argv[3] == 'orderNo' and sys.argv[6] == 'date':
    orderNo=sys.argv[4]
    destPath = sys.argv[5]
    dateStart = sys.argv[7]
    dateStop = sys.argv[8]
elif len(sys.argv)>5 and sys.argv[3] == 'orderNo':
    orderNo=sys.argv[4]
    destPath = sys.argv[5]
    dateStart = '1800'
    dateStop = '3000'
else:
    orderNo= '%'
    destPath = sys.argv[3]
    dateStart='1800'
    dateStop='3000'


print(("sys.argv[1] = "+sys.argv[1]))
print(("orderNo = "+str(orderNo)))
print(("dateStart = " + dateStart + "dateStop = " + dateStop))
print(("destPath = "+destPath))


if sys.argv[1] == 'obsId':
    print(("obsId="+str(sys.argv[2])))
    fileList = dbSpectro.getFilesSpcPerObsId(db, int(sys.argv[2]),orderNo)
elif sys.argv[1] == 'objectId':
    print(("objectId="+str(sys.argv[2])))
    fileList = dbSpectro.getFilesSpcPerObjIdDate(db, int(sys.argv[2]),orderNo,dateStart,dateStop)
else:
    print(("argument " + sys.argv[1] + " incorrect utiliser ObsId ou objectId"))
    db.close()
    exit(1)

json_text = open("../config/config.json").read()
config = json.loads(json_text)

PathBaseSpectro = config['path']['archive'] + '/archive'


print(("dossier source = "+ PathBaseSpectro))
print(("dossier destination = "+ destPath))

print("-----------------------")

i = 0
for f in fileList:
    i = i + 1
    fileSource = PathBaseSpectro + f[0] + '/' + f[1]
    fileDest = destPath + f[1]
    print(("fileSource = " + fileSource + "-->fileDest = " + fileDest))
    shutil.copy(fileSource, fileDest)
print((str(i) + " files extracted"))
db.close()
