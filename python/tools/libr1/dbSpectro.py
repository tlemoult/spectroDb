# module  spectrodbAccess.py
import MySQLdb,json
import datetime,time


def init_connection():
	json_text=open("../config/config.json").read()
	config=json.loads(json_text)
	db= MySQLdb.connect(config['db']['host'],config['db']['userName'],config['db']['password'],config['db']['dataBase'])
	print 'Init db connection, host=%s dataBase=%s'%(config['db']['host'],config['db']['dataBase'])
	return db

def commit_query_sql(db,query):
	print query
	cursor=db.cursor()
	cursor.execute(query)
	line=cursor.fetchone()
	try:
		return line[0]
	except:
		return 0

def commit_query_sql_table(db,query):
	print query
	cursor=db.cursor()
	cursor.execute(query)
	line=cursor.fetchone()
	try:
		return line
	except:
		return 0



#def get_instrument_from_id(db,Id):
#	query='SELECT * FROM instrum where instruId=%d'%(Id)
#	return commit_query_sql(db,query)

def getObjId_fromObjName(db,name):
	query='SELECT objectId from object where name="'+name+'"'
	return commit_query_sql(db,query)

def getObjId_fromRaDec(db,alpha,delta):
	query='SELECT objectId from object where alpha like "%s%s" and delta like "%s%s"'%(alpha[:8],'%',delta[:9],'%')
	return commit_query_sql(db,query)
	
def getObjName_fromRaDec(db,alpha,delta):
	query='SELECT name from object where alpha like "%s%s" and delta like "%s%s"'%(alpha[:8],'%',delta[:9],'%')
	return commit_query_sql(db,query)

def getObservationId_fromDateObs(db,dateObs):
	query='SELECT obsId from observation where DateObs="%s"'%(dateObs.strftime('%Y-%m-%d %H:%M:%S'))
	return commit_query_sql(db,query)
		
def getProjectId_fromProjectName(db,ProjectName):
	query='SELECT projectId from project where name="%s"'%(ProjectName)
	return commit_query_sql(db,query)

def getFileId_from_date(db,date):
	query='SELECT fileId FROM fileName where date="%s"'%(date.strftime('%Y-%m-%d %H:%M:%S'))
	return commit_query_sql(db,query)

def get_observerId_from_alias(db,observer):
	query='SELECT observerID from observer where alias="'+observer['alias']+'"'
	return commit_query_sql(db,query)

def get_observer_from_id(db,observerId):
	query='SELECT firstName,lastName,email,alias FROM observer where observerID=%d'%(observerId)
	result=commit_query_sql_table(db,query)
	observer={}
	observer['firstName']=result[0]
	observer['lastName']=result[1]
	observer['email']=result[2]
	observer['alias']=result[3]
	return observer

def get_site_from_id(db,siteId):
	query='SELECT name,lat,lon,alt,country,UAIcode FROM site where siteID=%d'%(siteId)
	result=commit_query_sql_table(db,query)
	site={}
	site['name']=result[0]
	site['lat']=result[1]
	site['lon']=result[2]
	site['alt']=result[3]
	site['country']=result[4]
	site['UAIcode']=result[5]
	return site

def get_siteId_from_name(db,site):
	siteName=site['name']
	query='SELECT siteId FROM site where name="%s"'%(siteName)
	return commit_query_sql(db,query)

def get_confInstru_fromId(db,instruId):
	query='SELECT name,telescop,spectro,resol,detector,guideDetector FROM instrum where instruId=%d'%(instruId)
	result=commit_query_sql_table(db,query)

	confInstru={}
	confInstru['configName']=result[0]
	confInstru['telescop']=result[1]
	confInstru['spectro']=result[2]
	confInstru['resol']=result[3]
	confInstru['detname']=result[4]
	confInstru['guideDetname']=result[5]
	return confInstru

def get_confObs_from_objId(db,objectId):
	query='SELECT timeSerie FROM object WHERE objectId=%d'%objectId
	result=commit_query_sql_table(db,query)
	return { 'timeSerie': result[0]}

def get_instruId_from_name(db,confInstru):
	confName=confInstru['configName']
	query='SELECT instruId FROM instrum where name="%s"'%(confName)
	return commit_query_sql(db,query)
		
def listObj(db):
	query = ("SELECT * FROM object")
	cursor= db.cursor()
	cursor.execute(query)
	print "object table"
	for l in cursor:
		print l

def listObs(db):
	query = ("SELECT * FROM observation")
	cursor= db.cursor()
	cursor.execute(query)
	print "observation table"
	for l in cursor:
		print l
		
def commit_insert_sql(db,sql):
	print "insert sql=",sql,
	cursor=db.cursor()
	try:
		cursor.execute(sql)
		db.commit()
		print '  insert (OK)'
		return True
	except:
		print '  insert (ERROR)'
		db.rollback()
		return False

def insert_observer(db,observer):
	sql="""INSERT INTO observer(firstName,lastName,email,alias)"""
	sql+=""" VALUES ('%s','%s','%s','%s')"""%(observer['firstName'],observer['lastName'],observer['email'],observer['alias'])
	commit_insert_sql(db,sql)
	return get_observerId_from_alias(db,observer)  # retourne l id juste insere

def insert_site(db,site):
	sql="""INSERT INTO site(name,country,lat,lon,alt,UAIcode)"""
	sql+=""" VALUES ('%s','%s','%s','%s','%s','%s')"""%(site['name'],site['country'],site['lat'],site['lon'],site['alt'],site['UAIcode'])
	commit_insert_sql(db,sql)
	return get_siteId_from_name(db,site) # retourne l id juste insere

def insert_InstrumConf(db,confInstru):
	sql="""INSERT INTO instrum(name,telescop,spectro,resol,detector,guideDetector)"""
	sql+=""" VALUES ('%s','%s','%s',%d,'%s','%s')"""%(confInstru['configName'],confInstru['telescop'],
												confInstru['spectro'],int(confInstru['resol']),confInstru['detname'],confInstru['guideDetname'])
	commit_insert_sql(db,sql)
	return get_instruId_from_name(db,confInstru)  # retourne l id juste insere

def insert_Obj(db,name,hd,alpha,delta):
	sql="""INSERT INTO object(name,noHD,alpha,delta) VALUES ('%s',%d,'%s','%s')"""% (name,hd,alpha,delta)
	commit_insert_sql(db,sql)

def update_Obj_info(db,cdsInfo,objID):

	sql="""UPDATE object SET """
	for k in ['bayerName','noHD','alpha','delta','OTYPE_V','FLUX_V','FLUX_B','FLUX_R','FLUX_K','FLUX_H','RV_VALUE','SP_TYPE','SP_QUAL','MK_Spectral_type']:
		if k in cdsInfo.keys():   # la clek existe
			if cdsInfo[k]!=None:   # elle n est pas vide
				if type(cdsInfo[k])==type(" "):
					sql+=k+"='"+str(cdsInfo[k])+"',"   # type string
				else:
					sql+=k+"="+str(cdsInfo[k])+","     # type nombre.
	sql=sql[:-1]  # enleve la virgule en trop
	sql+=""" WHERE objectId=%d"""%(objID)
	commit_insert_sql(db,sql)
	
def insert_Project(db,ProjectName):
	sql="""INSERT INTO project(name) VALUES ('%s')"""%(ProjectName)
	commit_insert_sql(db,sql)

def insert_Alias(db,objIdbyCoord,objName):
	query="""SELECT * from objalias where objId=%d and alias like '%s'"""%(objIdbyCoord,objName)
	if commit_query_sql(db,query)==0:
		print "   ajoute le nouveau alias : ",objName
		sql="""INSERT INTO objalias(objId,alias) VALUES ('%d','%s')"""%(objIdbyCoord,objName)
		commit_insert_sql(db,sql)
	else:
		print "   alias ",objName," deja connus"
def insert_filename(db,obsId,phase,destDir,f):
	if obsId==None: obsId='NULL'
	if f['binning']==None: f['binning']=''
	if f['ccdTemp']==None: f['ccdTemp']='NULL'
	if f['detector']==None: f['detector']=''

	sql="""INSERT INTO fileName(obsId,phase,filetype,filename,date,serieId,destDir,tempCCD,binning,detector)"""
	sql+=""" VALUES (%s,'%s','%s','%s','%s','%s','%s',%s,'%s','%s')"""%(str(obsId),phase,f['typ'],f['filename'],
															f['date'].strftime('%Y-%m-%d %H:%M:%S'),
															f['serieId'],destDir,str(f['ccdTemp']),str(f['binning']),str(f['detector']))
	commit_insert_sql(db,sql)
	
def insert_observation(db,projectId,objID,dateObs,isRef,observerId,instruId,siteId):
	if isRef:
		ref='R'
	else:
		ref=' '
	sql="""INSERT INTO observation(projectId,objId,dateObs,observerId,instruId,siteId,status,ref)
	VALUES (%d,%d,'%s',%d,%d,%d,'ACQFINISH','%s')"""%(projectId,objID,dateObs.strftime('%Y-%m-%d %H:%M:%S'),observerId,instruId,siteId,ref)
	commit_insert_sql(db,sql)

def insert_observation_with_name(db,ProjectName,objName,alpha,delta,dateObs,isRef,observerId,instruId,siteId):
	# verifie si l etoile est connue
	
	objIdbyName=getObjId_fromObjName(db,objName)
	if objIdbyName!=0:
		# objet connus par son nom
		print "Object connus par son nom ",objName
		isNewObject=False
		objId=objIdbyName
	
	else:
		objIdbyCoord=getObjId_fromRaDec(db,alpha,delta)
		if objIdbyCoord!=0:
			# object connus par ses coordonnes
			print "objet connus sous ces coordonnes",alpha,delta		
			isNewObject=False
			ObjNameFromRaDec=getObjName_fromRaDec(db,alpha,delta)
			if objName!=ObjNameFromRaDec:
				print "nouveau nom "+objName+" pour l objet connus sous le nom de "+ObjNameFromRaDec
				insert_Alias(db,objIdbyCoord,objName)
			else:
				print "Nom deja en base"
			objId=objIdbyCoord

		else:
			# object nouveau
			print "nouvel object en base suivant les coordonnes",alpha,delta
			isNewObject=True
			insert_Obj(db,objName,0,alpha,delta)
			objId=getObjId_fromRaDec(db,alpha,delta)
			
	

	# verifie le projet
	projectId=getProjectId_fromProjectName(db,ProjectName)
	if projectId==0:
		print "Projet",ProjectName,"nouveau, on le cree en base"
		insert_Project(db,ProjectName)
		projectId=getProjectId_fromProjectName(db,ProjectName)
	else:
		print "Projet",ProjectName,"connus"

	# insertion de l observation
	insert_observation(db,projectId,objId,dateObs,isRef,observerId,instruId,siteId)
	obsId=getObservationId_fromDateObs(db,dateObs)
	return (obsId,objId,isNewObject)



