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

def commit_query_sql_All_table(db,query):
	print query
	cursor=db.cursor()
	cursor.execute(query)
	return cursor

#def get_instrument_from_id(db,Id):
#	query='SELECT * FROM instrum where instruId=%d'%(Id)
#	return commit_query_sql(db,query)

def getFiles(db,dateDebut,dateFin):
	query="select fileName.destDir,fileId,fileName.filename,fileName.date from fileName "
	query+="where not fileName.filetype in ('JSON','FIELD') "
	query+="and date>'%s' and date <'%s' "%(dateDebut,dateFin)
	query+="order by fileName.date DESC"
	return commit_query_sql_All_table(db,query)

def getRequestToObserve(db):
	query="select project.name,RequestToObserveList.priority,object.name,alpha,delta,ExposureTime,"
	query+="NbExposure,TotExposure,intTime,object.FLUX_V,RequestToObserveList.uid,RequestToObserveList.config,RequestToObserveList.calib"
	query+=" from RequestToObserveList "
	query+="LEFT join object on RequestToObserveList.objectId=object.objectId "
	query+="LEFT join project on RequestToObserveList.projectId=project.projectId"
	return commit_query_sql_All_table(db,query)

