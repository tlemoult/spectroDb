import datetime,time
from datetime import datetime
import sys,os
import urllib.request, urllib.parse, urllib.error,glob
import libsdb.dbSpectro as dbSpectro
import libsdb.cds as cds #mes modules

print("Ajout demande observation dans la base")


configFilePath="../config/config.json"
db=dbSpectro.init_connection(configFilePath)
#dbSpectro.listObs(db)
#BasePath=sys.path[0]

if len(sys.argv)<5:
	print("nombre d'argument incorrect")
	print("""utiliser 4 arguments:  Projet 'nom_cds' priorite exposure""")
	exit(1)

project=sys.argv[1]
objname=sys.argv[2]
priority=int(sys.argv[3])
exposure=int(sys.argv[4])

print("verifie si object",objname,"est connus")
objId=dbSpectro.getObjId_fromObjName(db,objname)
if objId==0:
	print("nouvel objet")
else:
	print("object connus")

print('interroge le CDS obj="'+objname+'" ', end=' ')
cdsInfo=cds.getsimbadMesurement(objname)
if 'alpha' in list(cdsInfo.keys()):  # objet connus du CDS ?
	print(" OK")
	ra=cdsInfo['alpha']
	dec=cdsInfo['delta']
else:
	print(" Inconnus du CDS... On ne le prend pas dans la base")
	exit()

print("Insertion objet ",'"project="'+project+'"  objname="'+objname+'" ra="'+ra+'" dec="'+dec+'" priority=',priority,"exposure time=",exposure)

(objId,isNewObject)=dbSpectro.insert_request_observation_with_name(db,project,objname,ra,dec,priority,exposure)  #insert dans la base l observation

if isNewObject:
	print("Object "+objname+" inconnus, on update les donnees avec  mesures photometrique, type spectral, etc...")
	# complete avec les identifiant
	cdsname=cds.getHD_and_BayerIdentifier(objname)
	cdsInfo['bayerName']=cdsname['bayerName']
	cdsInfo['noHD']=cdsname['HDno']
	# update les mesures etc
	dbSpectro.update_Obj_info(db,cdsInfo,objId)  # complete les informations sur l objet.
else:
	print("Object "+objname+" connus")

db.close()

