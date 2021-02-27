import datetime
import time
import json
from datetime import datetime
import sys
import os
import shutil
import glob
import libsdb.dbSpectro as dbSpectro
import libsdb.cds as cds  # mes modules
from modEphem import * 

def createPath(racine,path):
	dirs=path.split("/")

	current=racine   # chemin absolu
	partDir=''				# chemin relatif
	for d in dirs:
		current=current+"/"+d
		partDir=partDir+"/"+d
		try:
			os.stat(current)
		except:
			os.mkdir(current)
	
	return (current,partDir)


print("Robot extrait les fichiers spectres RR Lyr traite")

objectId = 226  # RR Lyr in my data Base
#phiMin=0.2
#phiMax=0.4
phiMin=0.85
phiMax=0.96

directoryPerCycle=True

if len(sys.argv) !=7:
    print(" ordre 34 (Ha),  nomé Ha")
    print(" ordre 38 (He 5876),  nomé He5876")
    print(" ordre 48 (He 4686), nomé He4686")
    print("")
    print("nombre d'argument incorrect")
    print("utiliser: ")
    print("   python get-spc-RR.py orderNo 34 ./spectrum/RRlyr/34/ date 2019-12-31 2020-12-31")
    exit(1)

configFilePath="../../config/config.json"
db = dbSpectro.init_connection(configFilePath)
print("len(sys.argv)=" , len(sys.argv))

if len(sys.argv) == 7 and sys.argv[1] == 'orderNo' and sys.argv[4] == 'date':
    orderNo=sys.argv[2]
    destPath = sys.argv[3]
    dateStart = sys.argv[5]
    dateStop = sys.argv[6]

fileList = dbSpectro.getFilesSpcPerObjIdDate(db, objectId, orderNo, dateStart, dateStop)

json_text = open(configFilePath).read()
config = json.loads(json_text)

PathBaseSpectro = config['path']['archive'] + '/archive'

if orderNo == '34':
    orderDirPath = "Ha"
elif orderNo == '38':
    orderDirPath = "He5876_Na"
elif orderNo == '48':
    orderDirPath = "He4686"
else:
    orderDirPath = str(orderNo)

print(f"  objectId = {objectId}")
print(f"  orderNo = {orderNo}")
print(f"  phi = [{phiMin} ... {phiMax}]")
print(f"  dateStart = {dateStart}  dateStop = {dateStop}")
print(("  dossier source = "+ PathBaseSpectro))
print(("  dossier destination = "+ destPath))
if directoryPerCycle:
    print(f"     sous dossier par cycle: orderDirPath = {orderDirPath}")
else:
    print(f"     tous les cycles dans le meme dossier")

"""
Je prends usuellement 0.87 a 0.95.
"""

i = 0
pulseDict={}
for f in fileList:
    fileSource = PathBaseSpectro + f[0] + '/' + f[1]
    fileDest = destPath + f[1]
    dateUTC=f[2]
    jd=Time(dateUTC, scale='utc').jd
    phi = phase_RR_jd(jd)
    psi = phase_RR_blasko_jd(jd)
    nMax=int(jd/0.566793)-4333000

    if phi > phiMin and phi < phiMax:
        i = i +1
#        print(f"n = {nMax}, jd = {jd}, phi = {phi}, fileSource = {fileSource} --> fileDest = {fileDest}")
        if not str(nMax) in pulseDict:
            pathDirDatePsi = str(dateUTC)[0:10].replace("-","")+"_TLE_RC36_psi"+formatPhase(psi)[2:4]
            pulseDict[str(nMax)]={}
            if directoryPerCycle:
                pulseDict[str(nMax)]['pathDir']=pathDirDatePsi+"/"+orderDirPath
            else:
                pulseDict[str(nMax)]['pathDir']=orderDirPath
            pulseDict[str(nMax)]['files']=[]

        pulseDict[str(nMax)]['files'].append({"dirSrc":f[0] , "file": f[1] , "phi": phi})

       

print((str(i) + " files extracted"))
db.close()

for n in pulseDict.keys():
    print(f"n = {n},  pathDir = {pulseDict[n]['pathDir']}")

    createPath(destPath,pulseDict[n]['pathDir'])

    for oneFile in pulseDict[n]['files']:
        print(f"    dirSrc = {oneFile['dirSrc']}  file = {oneFile['file']}")
        fileSource = PathBaseSpectro + oneFile['dirSrc'] + '/' + oneFile['file']
        fileDest  = destPath + '/' + pulseDict[n]['pathDir'] + '/' + oneFile['file'].replace(".fits","_phi"+formatPhase(oneFile['phi'])[2:4]+".fit")
        print(f"fileSource = {fileSource} --> fileDest = {fileDest}")
        shutil.copy(fileSource, fileDest)

