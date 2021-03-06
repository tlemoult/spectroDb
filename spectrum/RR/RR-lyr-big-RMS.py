import libsdb.dbSpectro as dbSpectro
import json
from astropy.time import Time
import numpy
import astropy.io.fits as fits

print("Find spectrum with to big calibration RMS for RR lyr")

configFilePath="../../config/config.json"

db=dbSpectro.init_connection(configFilePath)
dbSpectro.setLogLevel(0)

# load configuration
json_text=open(configFilePath).read()
config=json.loads(json_text)
pathArchive=config['path']['archive']
print("pathArchive="+pathArchive)

objId=226  # RRlyr
spcFullLst=dbSpectro.getFile_from_type_obsId(db,objId,"'MULTIPLAN'")
for spcFull in spcFullLst:
    srcPath=pathArchive+'/archive'+spcFull[2]
    filename=spcFull[3]
    hduLst=fits.open(srcPath+'/'+filename)
    serieId=spcFull[1]
    for hdu in hduLst:
        if hdu.name=='ORDERS':
            data=hdu.data
            for l in data:
                if l[0]==34:
                    rms=l[20]
                    if rms>0.028:
                        print("WARNING %s  rms=%f"%(filename,rms))
                    else:
                        print("%s  rms=%f"%(filename,rms))

exit()
