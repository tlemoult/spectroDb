import datetime,time
from datetime import datetime
import sys,os
import urllib.request, urllib.parse, urllib.error,glob
#mes modules
import lib.dbSpectro as dbSpectro
import lib.fixHeader as fixHeader
import lib.archive as archive
import lib.cds as cds
import lib.myJson as myJson
import lib.emailFnc as emailFnc
import defineTimeSerie

print("Robot integration acquisition dans la base")

db=dbSpectro.init_connection()
archive.loadConfig()
#dbSpectro.listObs(db)
#BasePath=sys.path[0]

if len(sys.argv)<2:
	print("nombre d'argument incorrect")
	print("utiliser un arguments:  repertoire")
	print("Ou repertoire InstrumId")
	print("Ou repertoire InstrumId  ProjetName")
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
print("nom de dossier source : "+BasePath)
print("Configuration instrumentale par default: InstrumId= ",defaultInstruId, dbSpectro.get_confInstru_fromId(db,defaultInstruId))

# boucle sur les dossiers		
lstDir=fixHeader.listdirectory(BasePath)
for i in lstDir:
	print(i)

for dirSource in lstDir:
	instruId=defaultInstruId
	if dirSource==BasePath: continue  # on ne traite pas le dossier racine..
	print('-------------------------------------------------------\nEnter directory: "'+dirSource+'"')
	
	obsId=None  # pour le cas 'DARK, FLAT etc..' ou on a des fits d acquisition sans observation
	json=fixHeader.load_json(dirSource)
	if (json!=0):

		if json['statusObs']=='failed':
			print("statusObs=failed   Move")
			try:
				subject='[Carl]  Obs failed '
				subject+=json['target']['objname'][0]+' '+time.strftime("%A %d %B %Y %H:%M:%S")
				emailFnc.sendEmail(subject,"Your dear Carl.",db,json['project'])
			except:
				print("pb dans l envois de l email")
			print("Observation status=failed")
			archive.storeDir_Excep(dirSource,"Excep_observationFailed")
			continue  # on ne traite pas les observations en cours

		
		if json['statusObs']=='exposing':
			print("statusObs=exposing   Do not process")
			try:
				subject='[Carl] Obs start exposure '
				subject+=json['target']['objname'][0]+' '+time.strftime("%A %d %B %Y %H:%M:%S")
				emailFnc.sendEmail(subject,"Your dear Carl.",db,json['project'])
			except:
				print("pb dans l envois de l email")
			continue  # on ne traite pas les observations en cours


		if json['statusObs']!='finished':
			continue 
		# on traite que ce qui est finis

		#email sur l'observation
		try:
			msg=time.strftime("%A %d %B %Y %H:%M:%S")+"\n"
			msg+="Project Name="+json['project']+"\n"
			msg+="Target Name="+json['target']['objname'][0]+"\n"
			msg+="Coord\n"
			msg+="   RA="+json['target']['coord']['ra']+"\n"
			msg+="   DEC="+json['target']['coord']['dec']+"\n"
			msg+="Exposure: "+str(json['obsConfig']['NbExposure'])+" x "+str(json['obsConfig']['ExposureTime'])+" seconds.\n"
			msg+="Total Exposure: "+str(json['obsConfig']['TotalExposure'])+" seconds.\n"
			msg+="ConfigName="+json['instrument']['configName']+"\n"
		except:
			msg="Exception, No detail on observation\n"
		try:
			subject='[Carl] Obs finished '
			subject+=json['target']['objname'][0]+' '+time.strftime("%A %d %B %Y %H:%M:%S")
			emailFnc.sendEmail(subject,msg+"\nYour dear Carl.",db,json['project'])
		except:
			print("pb dans l envois de le mail")

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
			print("Configuration instrumentale connue, instruId=",instruId)
		else:
			print("Nouvelle Configuration instrumentale")
			instruId=dbSpectro.insert_InstrumConf(db,confInstru)

		# check site
		siteId=dbSpectro.get_siteId_from_name(db,site)
		if siteId!=0:
			print("Site observation connus, SiteId=",siteId)
		else:
			print("Nouveau Site d observation")
			siteId=dbSpectro.insert_site(db,site)
		
		# check observateur
		observerId=dbSpectro.get_observerId_from_alias(db,observer)
		if observerId!=0:
			print("Observateur connus, observerId=",observerId)
		else:
			print("Nouveau Observateur")
			observerId=dbSpectro.insert_observer(db,observer)
		
	else:
		print("    Json absent ou invalide, On se debrouille avec les fichiers fits, et les reglages par defaut")
		ra=""
		dec=""
		(objname,baseFileName,isRef)=fixHeader.get_obj_name_from_filename(dirSource)
		project=DefaultProject
		siteId=DefaultSiteId
		observerId=DefaultObserverId
		confInstru=dbSpectro.get_confInstru_fromId(db,instruId)
		observer=dbSpectro.get_observer_from_id(db,observerId)
		site=dbSpectro.get_site_from_id(db,siteId)
	
	print("Configuration retenue:")
	print("   instrument:",confInstru)
	print("   observer:",observer)
	print("   site:",site)
	print("*****************")
	
	if objname!='':   # arrive si on a que des darks , flat dans le dossier
		# identification de l object, pour ne pas inserer n importe quoi....
		print('interroge le CDS obj="'+objname+'" ', end=' ')
		try:
			cdsInfo=cds.getsimbadMesurement(objname)
			# retourne {} si le cds a repondu, mais objet inconnus.
			ra=cdsInfo['alpha']
			dec=cdsInfo['delta']
			print(" OK")
		except:
			print("Le cds ne repond pas ou objet inconnus")
			print(("Unexpected error:", sys.exc_info()[0]))
			cdsInfo={}
			print("    On regarde si il est connus de notre base")
			baseInfo=dbSpectro.getRaDecfromObjName(db,objname)
			if 'alpha' in list(baseInfo.keys()):
				print("    OK, object connus de notre base")
				ra=baseInfo['alpha']
				dec=baseInfo['delta']
			else:
				print("    Inconnus egalement de notre base, On ne le prend pas dans la base")
				archive.storeDir_Excep(dirSource,"Excep_UnknowObjectName") # exception...
				continue
		if json==0: myJson.write(dirSource,objname,isRef,ra,dec,project,confInstru,site,observer)
	else:
		print("Pas de cible, mais il peux y avoir d autres fichiers..")

	(isObservation,dateObs,returnedFileLST)=fixHeader.fix_header(objname,baseFileName,isRef,ra,dec,dirSource,confInstru)    # regarde les fichiers presents,  et fixe les Headers

	if isObservation:
		print("Observation objet trouve: ",'"project="'+project+'"  objname="'+objname+' isREf='+str(isRef)+'" ra="'+ra+'" dec="'+dec+'"')
		if (dbSpectro.getObservationId_fromDateObs(db,dateObs)==0):   # existe deja selon la date ?	
			(obsId,objId,isNewObject)=dbSpectro.insert_observation_with_name(db,project,objname,ra,dec,dateObs,isRef,observerId,instruId,siteId)  #insert dans la base l observation
					
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
		else:
			print('Observation deja existante "'+objname+'"'+"@"+str(dateObs))
			archive.storeDir_Excep(dirSource,"Excep_duplicate_obs")
			continue
	else:
		print("Pas d observation objet dans ce dossier.")


	if returnedFileLST!=[]:  # des que l on a des fichiers fits reconnus
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
				print("File: "+f['filename']+" @ "+str(f['date'])+' already in filename database')
				
		
		if isObservation:
			#redefine serieId si "time serie"
			timeSerie=dbSpectro.get_confObs_from_objId(db,objId)['timeSerie']
			if timeSerie=='YES':
				print("Redefine time Serie individual")
				defineTimeSerie.redefineTimeSerieObject([obsId],1)
				
			#copie les fichiers vers le pipeline de traitement
			archive.getFileRaw(returnedFileLST,destDir,obsId)
		
	else:
		print("No fits files here:")
db.close()

