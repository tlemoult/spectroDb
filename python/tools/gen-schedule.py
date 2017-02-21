
import lib.MyScheduler as MyScheduler
import lib.dbSpectro as dbSpectro
import astropy.units as u
from astropy.coordinates import SkyCoord
from datetime import date




schedule=MyScheduler.MySchedule()

db=dbSpectro.init_connection()

requests=dbSpectro.getRequestToObserve(db)
for request in requests:
	print request
	project=request[0]
	priority=request[1]
	name=request[2]
	ra=request[3].split(' ')
	dec=request[4].split(' ')
	coords=ra[0]+'h'+ra[1]+'m'+ra[2]+'s '+dec[0]+'d'+dec[1]+'m'+dec[2]+'s'
	FLUX_V=request[9]
	uid=request[10]
	conf=request[11]
	calib=request[12]
	
	if calib=='true':
		dureeCalibration=300
	else:
		dureeCalibration=60  # non nul, car contient la duree du recentrage, lancement guidage

	# duree et nombre de pose imposee
	if ((request[5]!=None) and (request[6]!=None)):
		ExposureTime=request[5]  # duree pose unitaire
		NbExposure=request[6]  # nombre de pose
		durationBlock=(ExposureTime*NbExposure+dureeCalibration)*u.second		
	else:
		ExposureTime=None
		NbExposure=None

	# Duree totale exposure	
	if request[7]!=None: 
		TotExposure=request[7] 
		durationBlock=(TotExposure+dureeCalibration)*u.second
	else: 
		TotExposure=None
	
	if request[8]!=None: intTime=request[8]  # duree integration pour time serie
	else: intTime=None
	

	config={ 'FLUX_V':FLUX_V,'project':project,'ExposureTime':ExposureTime,'NbExposure':NbExposure,
			 'TotExposure':TotExposure,'intTime':intTime,'uid':uid,'extraConf':conf,
			 'calib':calib
			}
	schedule.addTargetFromCoord(name,SkyCoord(coords),durationBlock,priority,config)


#stdExpo=1*3600*u.second
#priority=1
#config={ 'project':'Bess' }

#schedule.addTargetFromCoord('plasket',SkyCoord(ra=99.4621*u.deg, dec=6.6599417*u.deg),stdExpo,priority,config)
#schedule.addTargetFromCoord('deneb',SkyCoord(ra=93.4621*u.deg, dec=6.1599417*u.deg),stdExpo,priority,config)

#schedule.addTargetFromName('Deneb',stdExpo,priority,config)

schedule.optimize()

schedule.writeLst("schedule.lst")

schedule.showTable()
schedule.plotAirMas()

