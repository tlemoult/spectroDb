import sys,time, logging,json,os
import PyIndi

from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil

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

#load config
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
print(f"load configuration {configFilePath=}")
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logFilePath = config['path']['root']+config['path']['log']+'/'+config['logFile']
print(f"{logFilePath=}")
logging.basicConfig(filename=logFilePath,level=logging.DEBUG,format='%(asctime)s %(message)s')

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
J2000Target = myUtil.getCoordFromName("Spica")
obsSite=myUtil.getEarthLocation(config)
CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)
telescope.slewTelescope(CoordTelescopeTarget)

print("*********************")

#telescope use JNOW..   refracted..
#passer en alt az pour corriger de la refraction ?
#astrometry use J2000
coords = telescope.getCoordinates()
print(f"Actual telescope: coords = {coords}")
print("increase declinaison")
coords2 = SkyCoord(coords.ra,coords.dec + 1*u.deg,frame='icrs', equinox=Time.now())
print(f"New telescope: coords2 = {coords2}")
print("set telecope to the new coordinates")
telescope.syncCoordinates(coords2)

print("Wait some time")
time.sleep(4)

print("Re get coordinates")
coords = telescope.getCoordinates()
print(f"Telescope final coords:\n      {coords} \n        {coords.ra.hms}  {coords.dec.dms}")

telescope.disconnectServer()

exit()



