import requests,sys,time, logging,json
import PyIndi

from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil

from astropy import units as u
from astropy.coordinates import SkyCoord,FK5,AltAz,EarthLocation
from astropy.time import Time
from astropy.utils.iers import Conf as astropyConf

astropyConf.auto_download=False
json_text=open('./finder/confFinder.json').read()
config=json.loads(json_text)
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

finderHost = "localhost"
catalog = { "Vega" : "18h36m56.33635s&+38d47m01.2802s" , "Altair": "19h50m46.99855s&+08d52m05.9563s" , "Deneb":"20h41m25.91514s&+45d16m49.2197s","imgOK": "08h40m26.251922s&+36d27m00.1020804s" }

print("****** Initialize the finder and the telescope mount ****")

print("** Step 1: init the coord of mount with the Finder at previous optical centers we knows.")
r = requests.get(url = 'http://' + finderHost + ':5000/api/finder', params = {})
print(f"actual coords is = {r.json()}")

print(f"\n** Step 2: select a brigth stars from catalog:\n  {catalog.keys()}")
starName = input("type the star name: ")
if starName not in catalog.keys():
    print(f"{starName} is not in the catalog")
    exit()

coords = catalog [starName]
print(f"star name is {starName},  coords = {coords}")

print(f"** Step 3: We point this star")
telescope=Telescope(config['telescope'])
if not telescope.connect():
    print("Failed to connect Telescope")
    exit(1)
print("Telescope connected")

J2000Target = SkyCoord(coords.replace('&',' '), frame='icrs')
#J2000Target = myUtil.getCoordFromName("Spica")
obsSite=myUtil.getEarthLocation(config)
CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)
telescope.slewTelescope(CoordTelescopeTarget)

print(f"\n** Step 4: Put manualy the star in the slit")
input("then press ENTER")

print(f"** Step 5: We recalibrate the finder..")
r = requests.get(url = 'http://' + finderHost + ':5000/api/finder', params = {})
r = requests.get(url = 'http://' + finderHost + ':5000/api/finder/setCenter/'+coords, params = {})
data = r.json()
print(f"result {data}") 


