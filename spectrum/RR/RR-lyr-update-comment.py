import libsdb.dbSpectro as dbSpectro
import json
from astropy.time import Time
import numpy
import matplotlib.pyplot as plt 
from matplotlib import collections as mc

def formatPhase(phase):
    return "{:.2f}".format(round(phase, 2))


def phase_RR_jd(jd):

    ephem = { 
         '1994' : {'jd0': 2449572.4800   , 'per': 0.5668174} ,
         '2013' : {'jd0': 2456539.34275  , 'per': 0.5667975} ,
         '2014' : {'jd0': 2456914.5507   , 'per': 0.56684} ,
         '2015' : {'jd0': 2457286.3558   , 'per': 0.566793} ,
         '2016' : {'jd0': 2457597.5159   , 'per': 0.566793} ,
         '2017' : {'jd0': 2457861.6319   , 'per': 0.566793} ,
         '2018' : {'jd0': 2458349.6240   , 'per': 0.566793} ,
         '2019' : {'jd0': 2458709.5227   , 'per': 0.566793} ,
         '2020' : {'jd0': 2458976.4722   , 'per': 0.566793} ,
         'default' : {'jd0': 2456263.3118055556 , 'per':0.566782}
    }

    year=str(int(Time(jd , scale='tt',format='jd').to_value('jyear')))
    jd0=ephem[year]['jd0']
    per=ephem[year]['per']
    newPhi = (jd-jd0)/per
    newPhiFrac = newPhi - int(newPhi)
    if newPhiFrac<0:
        newPhiFrac=newPhiFrac+1

    return newPhiFrac

def phase_RR_blasko_jd(jd):

    ephem = {
        '1994' : {'jd0b': 2449631.312 , 'perb': 39.06 },
        '2013' : {'jd0b': 2456464.481, 'perb': 39.0},
        '2014' : {'jd0b': 2456881.627, 'perb': 39.0},
        '2015' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2016' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2017' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2018' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2019' : {'jd0b': 2457354.322, 'perb': 39.0},
        '2020' : {'jd0b': 2457354.322, 'perb': 39.0},
        'default' : {'jd0b': 2456846.489, 'perb': 39.0}
    }

    year=str(int(Time(jd , scale='tt',format='jd').to_value('jyear')))
    jd0b=ephem[year]['jd0b']
    perb=ephem[year]['perb']
    newPsi = (jd-jd0b)/perb
    newPsiFrac = newPsi - int(newPsi)
    if newPsiFrac<0:
        newPsiFrac=newPsiFrac+1

    return newPsiFrac

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
tableObsLatex=""

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
    #print(comment)
    dbSpectro.update_comment_obsId(db,obsId,comment)

    if jds[0]>2458847:  # if newer than january 2020
        #store data for plot
        x0=phase_RR_jd(jds[0])
        y0=jds[0]
        for jd in jds[1:]:
            #calc new point
            x1=phase_RR_jd(jd)
            y1=jd
            if x1<x0:
                #print("cuts")
                lines.append([ (x0,y0), (1,(y0+y1)/2)])
                lines.append([ (0,(y0+y1)/2), (x1,y1)])
            else:
                lines.append([ (x0,y0), (x1,y1)])
            #store
            x0=x1
            y0=y1

        #prepare latexTable
        tableObsLatex+=f"{str(dateUTC[0])[0:10]}  &  {int(jds[0])-2400000}" 
        tableObsLatex+="& 36 & Chelles &\\textsc{eShel V2} & 11\\,000 & 3.2 & $3\\,978-7\\,374$ " 
        tableObsLatex+=f"& xx & {formatPhase(begphi)} & {formatPhase(endphi)} & {formatPhase(phiBlasko)} "
        tableObsLatex+=f"& {len(dateUTC)} & 600 "
        tableObsLatex+="\\\\\n"



print("tableObsLatex:")
print(tableObsLatex)
print()

lc = mc.LineCollection(lines)
fig, ax = plt.subplots()
ax.add_collection(lc)
#ax.autoscale()
ax.margins(0.1)
ax.set_title('RR Lyr, Chelles 2020, observation, phases')
ax.set_ylabel('days(jd)')
ax.set_xlabel('pulsation phase')

plt.show()


