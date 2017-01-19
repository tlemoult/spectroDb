import datetime,time
from datetime import datetime
import sys,os
import urllib,glob
import dbSpectro,fixHeader,archive,cds,myJson  #mes modules



print "Robot integration acquisition dans la base"

db=dbSpectro.init_connection()
archive.loadConfig()
#dbSpectro.listObs(db)
#BasePath=sys.path[0]

if len(sys.argv)<2:
	print "nombre d'argument incorrect"
	print "utiliser un arguments:  repertoire"
	print "Ou repertoire InstrumId"
	print "Ou repertoire InstrumId  ProjetName"
	exit(1)

DefaultProject="none"
DefaultObserverId=1
DefaultSiteId=1
defaultInstruId=1

if len(sys.argv)==2:
	instruId=defaultInstruId
elif len(sys.argv)==3:
	defaultInstruId=int(sys.argv[2])
elif len(sys.argv)==4:
	defaultInstruId=int(sys.argv[2])
	DefaultProject=sys.argv[3]


BasePath=sys.argv[1]
print "nom de dossier source : "+BasePath
print "Configuration instrumentale par default: InstrumId= ",defaultInstruId, dbSpectro.get_confInstru_fromId(db,defaultInstruId)
exit()
# boucle sur les dossiers		
lstDir=fixHeader.listdirectory(BasePath)
for i in lstDir:
	print i

for dirSource in lstDir:
	instruId=defaultInstruId
	if dirSource==BasePath: continue  # on ne traite pas le dossier racine..
	print '-------------------------------------------------------\nEnter directory: "'+dirSource+'"'
	
	obsId=None  # pour le cas 'DARK, FLAT etc..' ou on a des fits d acquisition sans observation
	json=fixHeader.load_json(dirSource)
	if (json!=0):
		
		if json['statusObs']=='started':
			print "statusObs=started   Do not process"
			continue  # on ne traite pas les observations en cours
		
		ra=json['target']['coord']['ra']
		dec=json['target']['coord']['dec']
		objname=json['target']['objname'][0]
		try:
			isRef=json['target']['isRef']
		except:
			isRef=False
		baseFileName=objname
		project=json['project']
		confInstru=json['instrument']
		site=json['site']
		observer=json['observer']
		
		# check instrument
		instruId=dbSpectro.get_instruId_from_name(db,confInstru) # verifie si l on connait cette config
		if instruId!=0:
			print "Configuration instrumentale connue, instruId=",instruId
		else:
			print "Nouvelle Configuration instrumentale"
			instruId=dbSpectro.insert_InstrumConf(db,confInstru)

		# check site
		siteId=dbSpectro.get_siteId_from_name(db,site)
		if siteId!=0:
			print "Site observation connus, SiteId=",siteId
		else:
			print "Nouveau Site d observation"
			siteId=dbSpectro.insert_site(db,site)
		
		# check observateur
		observerId=dbSpectro.get_observerId_from_alias(db,observer)
		if observerId!=0:
			print "Observateur connus, observerId=",observerId
		else:
			print "Nouveau Observateur"
			observerId=dbSpectro.insert_observer(db,observer)
		
	else:
		print "    Json absent ou invalide, On se debrouille avec les fichiers fits, et les reglages par defaut"
		ra=""
		dec=""
		(objname,baseFileName,isRef)=fixHeader.get_obj_name_from_filename(dirSource)
		project=DefaultProject
		siteId=DefaultSiteId
		observerId=DefaultObserverId
		confInstru=dbSpectro.get_confInstru_fromId(db,instruId)
		observer=dbSpectro.get_observer_from_id(db,observerId)
		site=dbSpectro.get_site_from_id(db,siteId)
	
	print "Configuration retenue:"
	print "   instrument:",confInstru
	print "   observer:",observer
	print "   site:",site
	print "*****************"
	
	if objname!='':   # arrive si on a que des darks , flat dans le dossier
		print 'interroge le CDS obj="'+objname+'" ',
		cdsInfo=cds.getsimbadMesurement(objname)
		if 'alpha' in cdsInfo.keys():  # objet connus du CDS ?
			print " OK"
			ra=cdsInfo['alpha']
			dec=cdsInfo['delta']
		else:
			print " Inconnus du CDS... On ne le prend pas dans la base"
			archive.storeDir_Excep(dirSource,"Excep_UnknowObjectName") # exception...
			continue
		if json==0: myJson.write(dirSource,objname,isRef,ra,dec,project,confInstru,site,observer)
	else:
		print "Pas de cible, mais il peux y avoir d autres fichiers.."

	(isObservation,dateObs,returnedFileLST)=fixHeader.fix_header(objname,baseFileName,isRef,ra,dec,dirSource,confInstru)    # regarde les fichiers presents,  et fixe les Headers

	if isObservation:
		print "Observation objet trouve: ",'"project="'+project+'"  objname="'+objname+' isREf='+str(isRef)+'" ra="'+ra+'" dec="'+dec+'"'
		if (dbSpectro.getObservationId_fromDateObs(db,dateObs)==0):   # existe deja selon la date ?	
			(obsId,objId,isNewObject)=dbSpectro.insert_observation_with_name(db,project,objname,ra,dec,dateObs,isRef,observerId,instruId,siteId)  #insert dans la base l observation
					
			if isNewObject:
				print "Object "+objname+" inconnus, on update les donnees avec  mesures photometrique, type spectral, etc..."
				# complete avec les identifiant
				cdsname=cds.getHD_and_BayerIdentifier(objname)
				cdsInfo['bayerName']=cdsname['bayerName']
				cdsInfo['noHD']=cdsname['HDno']
				# update les mesures etc
				dbSpectro.update_Obj_info(db,cdsInfo,objId)  # complete les informations sur l objet.
			else:
				print "Object "+objname+" connus"
		else:
			print 'Observation deja existante "'+objname+'"'+"@"+str(dateObs)
			archive.storeDir_Excep(dirSource,"Excep_duplicate_obs")
			continue
	else:
		print "Pas d observation objet dans ce dossier."


	if returnedFileLST<>[]:  # des que l on a des fichiers fits reconnus
		# place en archive
		try:
			destDir=archive.moveFiles(dirSource,str(dateObs),returnedFileLST)   # deplace les fichiers reconnus,  supprime le reste...
		except:
			archive.storeDir_Excep(dirSource,"Excep_duplicate_dir")
			continue

		#met en base les nom de fichiers fits reconnus
		for f in returnedFileLST: 
			if dbSpectro.getFileId_from_date(db,f['date'])==0:  # si le fichier n existe pas, alors
				dbSpectro.insert_filename(db,obsId,'RAW',destDir,f)  
			else:
				print "File: "+f['filename']+" @ "+str(f['date'])+' already in filename database'
				
				
		#copie les fichiers vers le pipeline de traitement
		pathPipeline="/mnt/audela-pipe/raw"
		archive.getFileRaw(returnedFileLST,destDir,pathPipeline,obsId)

		
	else:
		print "No fits files here:"
db.close()

