from astropy.coordinates import EarthLocation
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
import astropy.utils.iers as iers

from astroplan import FixedTarget,observability_table,time_grid_from_range,is_observable
from astroplan import Observer,is_observable
from astroplan.constraints import AtNightConstraint, AirmassConstraint, TimeConstraint
from astroplan import ObservingBlock

def downloadPrecise():
	from astroplan import download_IERS_A
	download_IERS_A()

def jd_RR_phi(phase):
	return 2456263.311806+phase*0.566782

def phase_RR_jd(jd):
	return (jd-2456263.311806)/0.566782

def jd_RR_phi_blasko(phase):
	return 2457354.322+phase*39.0

def phase_RR_blasko_jd(jd):
	return (jd-2457354.322)/39.0

def disp_date(target,observer,times):
	fuseau=1*u.hour
	global_constraints = [AirmassConstraint(max = 3, boolean_constraint = False),AtNightConstraint.twilight_civil()]

	for time in times:
		if is_observable(global_constraints,observer,{target},[time])[0]:
			time.format = 'isot'
			print str(time)[:16]+'UTC  alt='+str(observer.altaz(time,target).alt)[:3],
			time.format = 'jd'
			print "jd=",time,
			jd=float(str(time))
			phase=phase_RR_jd(jd)
			print "phase=%.2f"%(phase-int(phase)),
			phase_blasko=phase_RR_blasko_jd(jd)
			print "& Blasko_Phase=%.2f"%(phase_blasko-int(phase_blasko)),
			time.format = 'isot'
			print "ObsTime=["+str(time+fuseau-1*u.hour)[11:16]+"TL,",str(time+fuseau+1*u.hour)[11:16]+"TL]",			
			print "<=> alt=["+str(observer.altaz(time-1*u.hour,target).alt)[:3]+".."+str(observer.altaz(time+1*u.hour,target).alt)[:3]+"]"

def getCurrentJDMod():
	t=Time.now()
	return int(t.jd-2455000)

locationChelles = EarthLocation.from_geodetic(2.581944444*u.deg, 48.88027778*u.deg, 50*u.m)
locationAix= EarthLocation.from_geodetic(5.445555*u.deg, 43.5209984*u.deg, 50*u.m)

location=locationChelles
observer = Observer(location=location, name="Chelles", timezone="UTC")



print "Observatory name=",observer.name,"location.lat=",location.latitude,"    location.lon=",location.longitude

coord=SkyCoord('19h25m27.911285s', '+42d47m03.6942s', unit=( u.hourangle,u.deg), frame='icrs')
target=FixedTarget(name='RR lyr', coord=coord)
#target=FixedTarget.from_name('RR lyr')  #interroge le CDS pour les coordonnes
print "target Name=",target.name
print " Coord:",
print  "ra.hms=",target.ra.hms," dec=",target.dec 

# l'heure
scanRange=range(getCurrentJDMod()-15,getCurrentJDMod()+15)
print "*********Phase 0.91 ********************"
t=[]
for j in scanRange:
	t.append(jd_RR_phi(j+0.91))
T=Time(t,format='jd', scale='utc')
disp_date(target,observer,T)

print "**********Phase 0.3 *************"
t=[]
for j in scanRange:
	t.append(jd_RR_phi(j+0.3))
T=Time(t,format='jd', scale='utc')
disp_date(target,observer,T)
