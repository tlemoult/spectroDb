import libsdb.dbSpectro as dbSpectro
import json
from astropy.time import Time
import numpy
import matplotlib.pyplot as plt 
from matplotlib import collections as mc


def phase_RR_jd(jd):
        if jd<2456657:   # avant 31 dec 2013
            phi=(jd-2456539.34275)/0.5667975   # ephem 2013
        elif jd<2457022.5:  # avant 31 dec 2014
            phi=(jd-2456914.5507)/0.56684  # ephem 2014
        elif jd<2458847.5:   # avant 30 dec 2019
            phi=(jd-2456263.3118055556)/0.566782
        else:
            phi=(jd-2458696.4843)/0.566782   # ephem du site pulsating star le 30 mai 2020

        return phi-int(phi)

def phase_RR_blasko_jd(jd):
        if jd<2456657:   # avant 31 dec 2013
            psi=(jd-2456464.481)/39.0
        elif jd<2457022.5:  # avant 31 dec 2014
            psi=(jd-2456881.627)/39.0   # ephem 2014
        else:
            psi=(jd-2457354.322)/39.0   # ephem 2015
        return psi-int(psi)

print("update observation comment field for RR lyr project.py")
configFilePath="../../config/config.json"
db=dbSpectro.init_connection(configFilePath)
dbSpectro.setLogLevel(0)

# load configuration
json_text=open(configFilePath).read()
config=json.loads(json_text)
pathArchive=config['path']['archive']
print("pathArchive="+pathArchive)

objId=226  # RRlyr
obsLst=dbSpectro.getObsIdFromObjId(db,objId)
print("observation Id")

lines=[]

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
    dateUTC.sort()
    #print(f"dateUTC={dateUTC}")
    jds=Time(dateUTC, scale='utc').jd
    jds.sort()
    #print(f"jds={jds}")
    jdmoy=numpy.mean(jds)

    # max min of phase
    #print(f"phi={[phase_RR_jd(j) for j in jds]}")
    endphi=phase_RR_jd(jds[-1])
    begphi=phase_RR_jd(jds[0])
    phiBlasko=phase_RR_blasko_jd(jdmoy)

    comment="psi=%.2f phi=%.2f,%.2f "%(phiBlasko,begphi,endphi)

    #store data for plot
    if jds[0]>2458847:  # newer than january 2020
        x0=phase_RR_jd(jds[0])
        y0=jds[0]
        for jd in jds[1:]:
            #calc new point
            x1=phase_RR_jd(jd)
            y1=jd
            if x1<x0:
                print("cuts")
                lines.append([ (x0,y0), (1,(y0+y1)/2)])
                lines.append([ (0,(y0+y1)/2), (x1,y1)])
            else:
                lines.append([ (x0,y0), (x1,y1)])
            #store 
            x0=x1
            y0=y1

    print(comment)

    dbSpectro.update_comment_obsId(db,obsId,comment)

lc = mc.LineCollection(lines)
fig, ax = plt.subplots()
ax.add_collection(lc)
#ax.autoscale()
ax.margins(0.1)
ax.set_title('RR Lyr, Chelles 2020, observation, phases')
ax.set_ylabel('days(jd)')
ax.set_xlabel('pulsation phase')

plt.show()


