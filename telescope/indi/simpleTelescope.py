import sys,time, logging,json
import PyIndi

from myLib.telescope import TelescopeClient as Telescope
import myLib.util as myUtil

from astropy import units as u
from astropy.coordinates import SkyCoord,FK5,AltAz,EarthLocation
from astropy.time import Time
from astropy.utils.iers import Conf as astropyConf

def testUtil():
    astropyConf.auto_download=False
    obsSiteChelles = EarthLocation(lat=48*u.deg+52*u.arcmin+49*u.arcsec,lon=2*u.deg+34*u.arcmin+55*u.arcsec,height=40*u.m)
    myUtil.convJ2000toJNowRefracted(myUtil.getCoordFromName('M33'),obsSiteChelles)



#########  main program here ####
### tested with astrophysics GTOCP2 driver
astropyConf.auto_download=False
json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
# create Telescope Client
telescope=Telescope(config['telescope'])

if not telescope.connect():
    exit(1)
print("Telescope connected")

print("Get coordinates")
coords = telescope.getCoordinates()
#c = SkyCoord(ra=coords['ra']*u.hourangle, dec=coords['dec']*u.degree, frame='icrs', equinox=Time.now())

print(f"Telescope initial coords:\n      {coords} \n       ra={coords.ra.hms}  dec={coords.dec.dms}")

#slew to a star
telescope.onCoordSet("TRACK")
J2000Target = myUtil.getCoordFromName("Spica")
obsSite=myUtil.getEarthLocation(config)
CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)
telescope.setCoordinates(CoordTelescopeTarget)
exit()


#telescope use JNOW..   refracted..
#passer en alt az pour corriger de la refraction ?
#astrometry use J2000
print("increase declinaison")
coords2 = SkyCoord(coords.ra,coords.dec + 1*u.deg,frame='icrs', equinox=Time.now())
print(f"New telescope: coords2 = {coords2}")
print("set new coordinates")
telescope.onCoordSet("SYNC")
telescope.setCoordinates(coords2)

print("Wait some time")
time.sleep(4)

print("Re get coordinates")
coords = telescope.getCoordinates()
print(f"Telescope final coords:\n      {coords} \n        {coords.ra.hms}  {coords.dec.dms}")

telescope.disconnectServer()

exit()



