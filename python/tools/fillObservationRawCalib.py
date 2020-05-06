import sys
import lib.dbSpectro as dbSpectro

def getClosestSerie(db,fileType,targetObsId,targetObsDate):

    print(("try to get "+fileType))
    files=dbSpectro.getFilesPerObsId(db,targetObsId,"""'"""+fileType+"""'""")
    countFile=0
    for file in files:
        countFile=countFile+1
    if countFile!=0:
        print((" -Already a serie of "+fileType+" in targetObsId = "+str(targetObsId)))
        return

    serieId,srcObsId=dbSpectro.getClosestSerieId(db,targetObsDate,fileType)
    if (srcObsId==targetObsId):
        print(("  Already a serie of "+fileType+" in targetObsId = "+str(targetObsId)))
        return
    else:
        print(("  Closest serie "+fileType+" of targetObsId = "+str(targetObsId)+" from observation srcObsId="+str(srcObsId)+""" serieId='"""+str(serieId))+"""'""")
        print(("  Link this this serie to obsId "+str(targetObsId)))
        dbSpectro.copySerieIdBetweenObsId(db,srcObsId,targetObsId,serieId)

    return


if len(sys.argv) < 2:
    print("nombre d'argument incorrect")
    print("utiliser: ")
    print("   python fillObservationRawCalib.py targetObsId")
    exit(1)

db = dbSpectro.init_connection()

targetObsId=int(sys.argv[1])

targetObsDate=dbSpectro.getObsDateFromObsId(db,targetObsId)
if targetObsDate==0:
    print(("targetObsId="+str(targetObsId)+" not found in database"))
    exit()
print(('targetObsId=%d'%targetObsId))
print(('targetObsDate=%s'%targetObsDate))

getClosestSerie(db,'CALIB',targetObsId,targetObsDate)
getClosestSerie(db,'TUNGSTEN',targetObsId,targetObsDate)
getClosestSerie(db,'LED',targetObsId,targetObsDate)


exit()
"""
select dateObs from observation where observation.obsId=2622;
select * from fileName where fileName.filetype='CALIB' and phase='RAW' and date>'2020-04-20 22:33:40' order by date limit 1 ;
select * from fileName where fileName.filetype='CALIB' and phase='RAW' and date<'2020-04-20 22:33:40' order by date desc limit 1 ;
"""

"""
INSERT INTO fileName 
SELECT fileName.fileId,fileName.md5sum, 3333 as obsId,fileName.phase, fileName.filetype, 
fileName.filename, fileName.serieId, fileName.expTime, fileName.date, fileName.destDir, 
fileName.tempCCD, fileName.binning, fileName.detector
from fileName 
where fileName.serieId='2020-04-16T23:25:28.41' and obsId=2618 order by filename;
"""
