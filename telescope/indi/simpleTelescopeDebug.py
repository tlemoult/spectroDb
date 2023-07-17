import sys,time, logging,json,os
import PyIndi

from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil

from astropy import units as u
from astropy.coordinates import SkyCoord,FK5,ICRS,AltAz,EarthLocation
from astropy.time import Time
from astropy.utils.iers import Conf as astropyConf

def testUtil():
    astropyConf.auto_download=False
    obsSiteChelles = EarthLocation(lat=48*u.deg+52*u.arcmin+49*u.arcsec,lon=2*u.deg+34*u.arcmin+55*u.arcsec,height=40*u.m)
    myUtil.convJ2000toJNowRefracted(myUtil.getCoordFromName('M33'),obsSiteChelles)

def coord_to_str(coords):
    raStr = str(coords.ra.to_string(u.hour,precision=2))
    decStr = str(coords.dec.to_string(u.degree, alwayssign=True,precision=2))
    return f"{raStr} {decStr}"

def coord_equinox_Test(star_name):

    # Coordonnées de l'étoile
    star_coord = SkyCoord.from_name(star_name)
    print(f"{star_name} J2000 {coord_to_str(star_coord)}")

    # Coordonnées dans l'équinoxe JNOW
    time_now = Time.now()
    star_coord_jnow = star_coord.transform_to(FK5(equinox=time_now)) 
    print(f"{star_name} JNOW={time_now}  {coord_to_str(star_coord_jnow)}")

    observatory = EarthLocation(lat=48*u.deg+52*u.arcmin+49*u.arcsec,lon=2*u.deg+34*u.arcmin+55*u.arcsec,height=40*u.m)
    coord_jnow_refrac = myUtil.convJ2000toJNowRefracted(star_coord,observatory)
    print(f"{star_name} JNOW REFRAC={time_now}  {coord_to_str(coord_jnow_refrac)}")

#########  main program here ####

### tested with astrophysics GTOCP2 driver
astropyConf.auto_download=False

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
print(f"Configuration file is {configFilePath}")
json_text=open(configFilePath).read()
config = json.loads(json_text)

# setup log file
logging.basicConfig(filename=config["path"]["root"] + config["path"]["log"]+'/'+config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

# create Telescope Client
telescope=Telescope(config['telescope'])

if not telescope.connect():
    exit(1)
print("Telescope connected")

print("Get coordinates")
coords_telescope = telescope.getCoordinates()
print(f" Telescope initial coords: {coord_to_str(coords_telescope)}")

print("sync with the same coordinate")
telescope.syncCoordinates(coords_telescope)
time.sleep(1)

new_coord_tel = telescope.getCoordinates()
print(f"get again coordinates form telescope: {coord_to_str(new_coord_tel)}")
sep = coords_telescope.separation(new_coord_tel)
print(f"separate : {sep},  or {sep.arcminute} arcmin  {sep.arcsecond}  arcsecond")

exit()

for i in range(5):
    oldCoords = coords
    coords = telescope.getCoordinates()
    sep = coords.separation(coords)
    print(f"separate : {sep},  or {sep.arcminute} arcmin  {sep.arcsecond}  arcsecond")
    disp_coord("telescope JNow",coords)
    time.sleep(1)


#    telescope.syncCoordinates(coords)
#coords2 = telescope.getCoordinates()
#print(f"Actual telescope: coords2 JNow = {coords2}")

telescope.disconnectServer()
time.sleep(0.5)

exit()



