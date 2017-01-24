import datetime,time,json
from datetime import datetime
import sys,os,shutil
import urllib,glob
import pyfits
import lib.dbSpectro as dbSpectro
import lib.cds as cds #mes modules

def main():
	print "redefinie les time serie"

	if len(sys.argv)<3:
		print "nombre d'argument incorrect"
		print "utiliser: "
		print "    python define-time-serie.py ObsId NbRawPerStack"
		print "ou  python define-time-serie.py range obsIdStart obsIdStop NbRawPerStack"
		exit(1)

	if len(sys.argv)==3:
		obsIds=[int(sys.argv[1])]
		NbRawPerStack=int(sys.argv[2])
		redefineTimeSerieObject(obsIds,NbRawPerStack)
	elif len(sys.argv)==5 and sys.argv[1]=='range':
		obsIds=range(int(sys.argv[2]),int(sys.argv[3])+1)
		NbRawPerStack=int(sys.argv[4])
		redefineTimeSerieObject(obsIds,NbRawPerStack)
	else:
		print "arguments incorrects"
		exit()


def redefineTimeSerieObject(obsIds,NbRawPerStack):
	json_text=open("../config/config.json").read()
	config=json.loads(json_text)
	PathBaseSpectro= config['path']['archive']+'/archive'

	db=dbSpectro.init_connection()

	print "obsIds=",obsIds
	print "NbRawPerStack=",NbRawPerStack

	for obsId in obsIds:
		print "process obsId=",obsId
		fileList=dbSpectro.getFilesPerObsId(db,obsId,"""'OBJECT'""")
		print "-----------------------"

		i=1
		for row in fileList:
			print row
			fileSource=PathBaseSpectro+row[0]+'/'+row[2]
			fileDest=fileSource+".tmp"
			
			fileId=row[1]
			fileDate=row[3]
			serieId=row[4]


			hdulist = pyfits.open(fileSource)
			prihdr  = hdulist[0].header

			if i==1:  # au premier passage
				newSerieId=str(fileDate).replace(' ','T')

			if i==NbRawPerStack:
				i=1
			else:
				i=i+1
				
			prihdr['SERIESID']=newSerieId

			print "fileId=",fileId,"fileDate=",fileDate,"serieId=",serieId, "New SerieId=",newSerieId
			print "fileSource",fileSource
			print "fileDest",fileDest
			print 

			dbSpectro.update_files_serieId(db,fileId,newSerieId)

			hdulist.writeto(fileSource+'tmp')  # ecris fichier tmps
			hdulist.close(fileSource)		   # ferme initial
			os.remove(fileSource)              # efface initial
			os.rename(fileSource+'tmp',fileSource) # renome 


		print "------------------------"

	print "Fin du robot"
	db.close()

if __name__ == '__main__':
    main()