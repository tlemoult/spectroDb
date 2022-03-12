import sys,time, logging,json
import PyIndi

from myLib.telescope import TelescopeClient as Telescope

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

#load configuration
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
c = SkyCoord(ra=coords['ra']*u.hourangle, dec=coords['dec']*u.degree, frame='icrs', equinox=Time.now())
print(f"Initial coords:\n{coords} \n{c.ra.hms}  {c.dec.dms}")

#telescope use JNOW..   refracted..
#passer en alt az pour corriger de la refraction ?
#astrometry use J2000

exit()
print("increase declinaision")
coords['dec'] = coords['dec'] - 1

print("set new coordinates")
telescope.setCoordinates(coords)

print("Wait some time")
time.sleep(4)

print("Re get coordinates")
coords = telescope.getCoordinates()
c = SkyCoord(ra=coords['ra']*u.hourangle, dec=coords['dec']*u.degree, frame='icrs')
print(f"final coords:\n{coords} \n{c.ra.hms}  {c.dec.dms}")






