import lib.dbSpectro as dbSpectro
import json,sys,shutil
from astropy.time import Time
import numpy


def pulsating_phase_RR(dateUTC):
    jd=Time(dateUTC, scale='utc').jd
    year=dateUTC.year
    if year=='1994':
        #~~ Pour publi :
        #-- POUR 1996-97 : (Hubscher et al., 1998)
        jd0p=2450456.7090
        periodep=0.5668174
    elif year=='1996':
        #~~ Pour publi :
        #-- POUR 1996-97 : (Hubscher et al., 1998) old=2446654.368+0.566839E
        jd0p=2450456.7090
        periodep=0.5668174
    elif year=='1997':
        #~~ Pour publi :
        #-- POUR 1996-97 : (Hubscher et al., 1998)
        jd0p=2450456.7090
        periodep=0.5668174
    elif year=='2013':
        #-- Gillet 20160805 : T0 sur GEOS et P sur Le Borgne 2014
        #~~ Pour publi :
        #- POUR 2013 :
        jd0p=2456539.34275 ; # Max recent 2013=2013 9 3 20 13 33.599986 => pour 2013
        periodep=0.5667975 ; # Periode dans un intervalle "P0 shorter" (Le Borgne 2014) => pour 2013
    elif year=='2014':
        #~~ Pour publi :
        #- POUR 2014 :
        jd0p=2456914.5507 ; # Max recent 2014=2014 9 14 1 13 0.480002 => pour 2014
        periodep=0.56684 ; # Periode dans un intervalle "P0 longer" (Le Borgne 2014) => pour 2014
    elif year=='2017':
        #~~ Pour publi :
        #- POUR 2017 :
        jd0p=2457861.6319 ; 
        periodep=0.566793 ;    
    else:
        #~~ Pour usuel :
        #-- Daniel Verillac habituelle BEST : JD0=1/12/2012T19:29:00=2456263.3118055556, P=0,566782
        #-- Periode AAVSO : 0.56686776
        jd0p=2456263.3118055556
        periodep=0.566782

    return (jd-jd0p)/periodep

def phase_RR_blasko_jd(dateUTC):
    jd=Time(dateUTC, scale='utc').jd
    if jd<2456657:   # avant 31 dec 2013
        return (jd-2456464.481)/39.0
    elif jd<2457022.5:  # avant 31 dec 2014
        return (jd-2456881.627)/39.0   # ephem 2014
    else:
        return (jd-2457354.322)/39.0   # ephem 2015

objId=226  # RRlyr
orderNo=34  # H alpha order
phiMin=0.85
phiMax=0.95
print("get RR lyrae spectrum for defined pulsating phase")
print("phiMin="+str(phiMin)+" phiMax="+str(phiMax))
print("len(sys.argv)=" , len(sys.argv))
print("argv=",sys.argv)
if len(sys.argv)<>2:
    print("use destination path as first argument")
    exit()
else:
	destPath = sys.argv[1]

db=dbSpectro.init_connection()
dbSpectro.setLogLevel(0)

# load configuration
json_text=open("../config/config.json").read()
config=json.loads(json_text)
PathBaseSpectro = config['path']['archive'] + '/archive'

fileList = dbSpectro.getFilesSpcPerObjId(db, objId,orderNo)

i=0
for f in fileList:
    fileSource = PathBaseSpectro + f[0] + '/' + f[1]
    fileDest = destPath + f[1]
    dateObs=f[2]
    phi=pulsating_phase_RR(dateObs)%1
    if phiMin<phi<phiMax:
        i = i + 1
        print(str(dateObs)+" phi="+str(phi))+" "+str(f[1])
        print "fileSource", fileSource, "-->fileDest", fileDest
        shutil.copy(fileSource, fileDest)

print str(i) + " files extracted"
db.close()
