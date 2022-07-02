from astropy import units as u
from astropy.coordinates import SkyCoord,FK5,AltAz,EarthLocation
from astropy.time import Time
from astropy.utils.iers import Conf as astropyConf

def getEarthLocation(config):
    obsSite=config["obsSite"]
    obsLat=obsSite['latDeg']*u.deg+obsSite['latMin']*u.arcmin+obsSite['latSec']*u.arcsec
    obsLon=obsSite['lonDeg']*u.deg+obsSite['lonMin']*u.arcmin+obsSite['lonSec']*u.arcsec
    return EarthLocation(lat=obsLat,lon=obsLon,height=obsSite['altitude']*u.m)

def getCoordFromName(name):
    c = SkyCoord.from_name(name)
    print(f"getCoordFromName  name = {name} :\n      {c.ra.hms}  {c.dec.dms}")
    return c

def convJ2000toJNowRefracted(skyCoords,obsSite,pressure=101700*u.pascal,temperature=5*u.Celsius):
    c = skyCoords
    t = Time.now()
    print(f"Enter convJ2000toJNowRefracted()")
    print(f"SkyCoords equinox J2000: {c}\n     {c.ra.hms}  {c.dec.dms}")
    
    cJNow = c.transform_to(FK5(equinox=t))
    print(f"SkyCoords equinox Now:   {cJNow}\n     {cJNow.ra.hms}  {cJNow.dec.dms}")

    cAltAz = c.transform_to(AltAz(obstime=t,location=obsSite))
    print(f"SkyCoords AltAz: {cAltAz}\n")

    cAltAzRefrac = c.transform_to(AltAz(obstime=t,location=obsSite,pressure=pressure,temperature=temperature,relative_humidity=0.8,obswl=0.65*u.micron))
    print(f"SkyCoords cAltAzRefrac: {cAltAzRefrac}\n")
    cAltAzRefracTric = AltAz(obstime=t,location=obsSite,alt=cAltAzRefrac.alt,az=cAltAzRefrac.az)
    cJNowRefractedTric = cAltAzRefracTric.transform_to(FK5(equinox=t))
    print(f"Skycoods cJNowRefacted = {cJNowRefractedTric}\n     {cJNowRefractedTric.ra.hms}  {cJNowRefractedTric.dec.dms}")
    print(f"  Refraction delta is {abs(cAltAz.alt-cAltAzRefrac.alt).value*60:.1f} arcminutes")
    return cJNowRefractedTric

if __name__ == '__main__':
    print("Demo of util lib")
    astropyConf.auto_download=False
    obsSiteChelles = EarthLocation(lat=48*u.deg+52*u.arcmin+49*u.arcsec,lon=2*u.deg+34*u.arcmin+55*u.arcsec,height=40*u.m)

    convJ2000toJNowRefracted(getCoordFromName('M33'),obsSiteChelles)
