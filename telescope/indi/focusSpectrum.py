import sys,time, logging,json
import PyIndi
from astropy.io import fits
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt

from libindi.camera import CameraClient as CamSpectro

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
json_text=open(configFilePath).read()
config = json.loads(json_text)

path= config['path']['root']+'/'+config['path']['focus']

# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
# create and connect to Camera 
camSpectro=CamSpectro(config["ccdSpectro"])
camSpectro.setBinning({'X':3,'Y':3})

#acquisition
print("run acquisition")
exposureTime = 10
camSpectro.newAcquSerie(path,"FOCUS-",1,exposureTime)
camSpectro.waitEndAcqSerie()
print("acquisition finished")

# stat
filename = path+"/FOCUS-1.fits"
hdulist = fits.open(filename)
print(hdulist.info())
print("clean hot pixel with median filter")
img=ndimage.median_filter(hdulist[0].data,3)

spectrumLine = 346
spectrumHeight = 25
lineStart = spectrumLine - spectrumHeight//2
lineStop = spectrumLine + spectrumHeight//2
imgUse = img[lineStart:lineStop,150:800]
print(f"Extract zone lines [{lineStart}:{lineStop}]")
print(f"Mean = {np.mean(imgUse)}   Max = {np.max(imgUse)}")


plt.imshow(imgUse, cmap=plt.cm.gray) 
plt.show()


