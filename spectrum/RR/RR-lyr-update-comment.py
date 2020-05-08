import lib.dbSpectro as dbSpectro
import json
from astropy.time import Time
import numpy


def phase_RR_jd(jd):
        if jd<2456657:   # avant 31 dec 2013
            return (jd-2456539.34275)/0.5667975  # ephem 2013
        elif jd<2457022.5:  # avant 31 dec 2014
            return (jd-2456914.5507)/0.56684  # ephem 2014
        else:
        	return (jd-2456263.3118055556)/0.566782

def phase_RR_blasko_jd(jd):
        if jd<2456657:   # avant 31 dec 2013
            return (jd-2456464.481)/39.0
        elif jd<2457022.5:  # avant 31 dec 2014
            return (jd-2456881.627)/39.0   # ephem 2014
        else:
            return (jd-2457354.322)/39.0   # ephem 2015

print("update observation comment field for RR lyr project.py")

db=dbSpectro.init_connection()
dbSpectro.setLogLevel(0)

# load configuration
json_text=open("../config/config.json").read()
config=json.loads(json_text)
pathArchive=config['path']['archive']
print("pathArchive="+pathArchive)

objId=226  # RRlyr
obsLst=dbSpectro.getObsIdFromObjId(db,objId)
print("observation Id")
for obsIdt in obsLst:
    obsId=obsIdt[0]
    print("obsId=%d "%obsId, end=' ')
    obsExposureObjectLst=dbSpectro.getObsDateLstFromObsId(db,obsId)

    # transform 2D tuple in 1D
    dateUTC=[]
    for obsExposureObjectt in obsExposureObjectLst:
        date=obsExposureObjectt[0]
        dateUTC+=[date]

    # convert in jd
    #print "dateUTC=",dateUTC
    jds=Time(dateUTC, scale='utc').jd
    #print "jds=",jds
    jdmoy=numpy.mean(jds)

    # max min of phase
    maxphi=max(jds,key=phase_RR_jd)
    maxphi=maxphi-int(maxphi)
    minphi=min(jds,key=phase_RR_jd)
    minphi=minphi-int(minphi)

    phiBlasko=phase_RR_blasko_jd(jdmoy)
    phiBlasko=phiBlasko-int(phiBlasko)

    comment="psi=%.2f phi=%.2f,%.2f "%(phiBlasko,minphi,maxphi)
    
    print(comment)

    dbSpectro.update_comment_obsId(db,obsId,comment)
