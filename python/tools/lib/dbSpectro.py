# module  spectrodbAccess.py
import MySQLdb,json
import datetime,time



def init_connection():
	global logLevel
	logLevel=0
	json_text=open("../config/config.json").read()
	config=json.loads(json_text)
	db= MySQLdb.connect(config['db']['host'],config['db']['userName'],config['db']['password'],config['db']['dataBase'])
	print 'Init db connection, host=%s dataBase=%s'%(config['db']['host'],config['db']['dataBase'])	
	return db

def setLogLevel(n):
	global logLevel
	print "loglevel=",n
	logLevel=n
	return 1

def commit_query_sql(db,query):
	global logLevel
	if logLevel>2: print query
	cursor=db.cursor()
	cursor.execute(query)
	line=cursor.fetchone()
	try:
		return line[0]
	except:
		return 0

def commit_query_sql_table(db,query):
	global logLevel
	if logLevel>2: print query
	cursor=db.cursor()
	cursor.execute(query)
	line=cursor.fetchone()
	try:
		return line
	except:
		return 0

def commit_query_sql_All_table(db,query):
	global logLevel
	if logLevel>2: print query
	cursor=db.cursor()
	cursor.execute(query)
	return cursor

#def get_instrument_from_id(db,Id):
#	query='SELECT * FROM instrum where instruId=%d'%(Id)
#	return commit_query_sql(db,query)

def getObjId_fromObjName(db,name):
	query='SELECT objectId from object where name="'+name+'"'
	return commit_query_sql(db,query)

def getDirectory_from_STRdate(db,date):
	query='SELECT destDir,obsId FROM fileName where phase="RAW" and filetype="OBJECT" and date="%s"'%(date.replace('T',' ')[:19])
	result=commit_query_sql_table(db,query)
	print "result",result
	if result=='None':
		return {}

	try:
		return {'path':result[0].split('/raw')[0],'obsId':result[1]}
	except:
		return {}
		
def commit_insert_sql(db,sql):
	global logLevel
	print "logLevel=",logLevel
	if logLevel>2: print "insert sql=",sql,
	cursor=db.cursor()
	try:
		cursor.execute(sql)
		db.commit()
		if logLevel>2: print '  insert (OK)'
		return True
	except:
		print '  insert (ERROR)'
		db.rollback()
		return False


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
	
def getProjectId_fromProjectName(db,ProjectName):
	query='SELECT projectId from project where name="%s"'%(ProjectName)
	return commit_query_sql(db,query)
	
def insert_request_observation(db,projectId,objId,priority,exposure):
	sql="""INSERT INTO RequestToObserveList(projectId,objectId,priority,TotExposure)
	VALUES (%d,%d,%d,%d)"""%(projectId,objId,priority,exposure)
	commit_insert_sql(db,sql)

def insert_request_observation_with_name(db,ProjectName,objName,alpha,delta,priority,exposure):
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
	insert_request_observation(db,projectId,objId,priority,exposure)
	return (objId,isNewObject)

def getFilesPerObsId(db,obsId,fileTypeLst): # 'OBJECT','CALIB','TUNGSTEN','LED'
	query="select fileName.destDir,fileId,fileName.filename,fileName.date,fileName.serieId from fileName "
	query+="where fileName.filetype in (%s)"%fileTypeLst
	query+="and obsId=%d "%(obsId)
	query+="order by fileName.date ASC"
	return commit_query_sql_All_table(db,query)

def getPathFilename_from_md5sum(db,md5sum):
	query="select fileName.destDir,fileName.filename from fileName "
	query+="""where fileName.md5sum='%s' """%md5sum
	return commit_query_sql_table(db,query)


def update_files_serieId(db,fileId,serieId):
	sql="""UPDATE fileName SET """
	sql+="""serieId='"""+serieId+"""'"""
	sql+=""" WHERE fileId=%d"""%(fileId)
	
	commit_insert_sql(db,sql)

def insert_filename_meta(db,meta):

	if 'obsId' not in meta.keys():
		print "ignore this, obsId not defined."+ json.dumps(meta,sort_keys=True, indent=4)
		return

	if meta['fileType']=='1DSPECTRUM':
		if 'BSS_ORD' in meta.keys():
			orderSuffix="'"+meta['destinationBSS_ORD']+"'"
		else:
			orderSuffix='NULL'

		sql="""INSERT INTO fileSpectrum(obsId,filename,path,"""
		sql+="""dateObs,filetype,expTime,lStart,lStop,"""
		sql+="""md5sum,naxis1,orderNo,orderSuffix)"""
		sql+=""" VALUES (%s,'%s','%s',  '%s','%s',%s,%s,%s,  '%s',%s,'%s',%s)"""%(meta['obsId'],meta['destinationFilename'],meta['destinationPath'],
															meta['dateObs'].replace('T',' '),meta['fileType'],meta['expTime'],meta['lStart'],meta['lStop'],
															meta['md5sum'],meta['naxis1'],str(meta['order']),orderSuffix)
		commit_insert_sql(db,sql)

	else:
		print "normal file destinationFile="+ meta['destinationFilename']

		if 'detector' in meta.keys(): detector="'"+meta['detector']+"'" 	
		else:  detector='NULL'
		if 'tempCCD' in meta.keys(): tempCCD=meta['tempCCD'] 				
		else: tempCCD='NULL'
		if 'binning' in meta.keys(): binning="'"+meta['binning']+"'"		
		else: binning='NULL'

		sql="""INSERT INTO fileName(obsId,filename,destDir,"""
		sql+="""date,filetype,md5sum,phase,"""
		sql+="""binning,detector,tempCCD)"""
		sql+=""" VALUES (%s,'%s','%s',  '%s','%s','%s','DATA',  %s,%s,%s)"""%(meta['obsId'],meta['destinationFilename'],meta['destinationPath'],
															meta['dateObs'].replace('T',' '),meta['fileType'],meta['md5sum'],
															binning,detector,tempCCD)
		commit_insert_sql(db,sql)


