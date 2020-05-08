import json,sys,os,shutil
import astropy.io.fits as fits
import lib.dbSpectro as dbSpectro

print("retablis les temps d exposition dans la base de donne")

json_text=open("../config/config.json").read()
config=json.loads(json_text)

PathBaseSpectro= config['path']['archive']+'/archive'

print("dossier source",PathBaseSpectro)

db=dbSpectro.init_connection()

table=dbSpectro.getAllFileIdFileName(db,""" "TUNGSTEN","FIELD","OBJECT","LED","CALIB","DARK","BIAS","NEON","FLAT","PRNU","MULTIPLAN","2DSPECTRUM","REPONSE" """)

for row in table:
	r={'fileId':row[0],'phase':row[1],'path':row[2],'filename':row[3]}
	print(r)
	try:
		hdulist = fits.open(PathBaseSpectro+r['path']+"/"+r['filename'])
		prihdr  = hdulist[0].header
		expTime=float(prihdr['EXPOSURE'])
	except:
		expTime=0
	print("Update EXPOSURE=",expTime)
	dbSpectro.update_expTime_fileId(db,r['fileId'],expTime)

db.close()

