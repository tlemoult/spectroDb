import lib.dbSpectro as dbSpectro
import json
from astropy.time import Time
import numpy


def phase_RR_jd(jd):
    	return (jd-2456263.311806)/0.566782

def phase_RR_blasko_jd(jd):
    	return (jd-2457354.322)/39.0

print "update observation comment field for RR lyr project.py"

db=dbSpectro.init_connection()
dbSpectro.setLogLevel(0)

# load configuration
json_text=open("../config/config.json").read()
config=json.loads(json_text)
pathArchive=config['path']['archive']
print "pathArchive="+pathArchive

objId=226  # RRlyr
obsLst=dbSpectro.getObsIdFromObjId(db,objId)
print "observation Id"
for obsIdt in obsLst:
    obsId=obsIdt[0]
    print "obsId=%d "%obsId,
    obsExposureObjectLst=dbSpectro.getObsDateLstFromObsId(db,obsId)

    # transform 2D tuple in 1D
    dateUTC=[]
    for obsExposureObjectt in obsExposureObjectLst:
        date=obsExposureObjectt[0]
        dateUTC+=[date]

    # convert in jd
    jds=Time(dateUTC, scale='utc').jd
    jdmoy=numpy.mean(jds)

    # max min of phase
    maxphi=max(jds,key=phase_RR_jd)
    maxphi=maxphi-int(maxphi)
    minphi=min(jds,key=phase_RR_jd)
    minphi=minphi-int(minphi)

    phiBlasko=phase_RR_blasko_jd(jdmoy)
    phiBlasko=phiBlasko-int(phiBlasko)

    comment="PHI=%.2f phi:[%.2f,%.2f] "%(phiBlasko,minphi,maxphi)
    
    print comment

    dbSpectro.update_comment_obsId(db,obsId,comment)
