import sys,time,os, logging,json
import PyIndi
from astropy.io import fits
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt

from libindi.camera import CameraClient as CamSpectro
from libobs import astrosib as astrosib
from libcalc.img import statSpectrum

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
json_text=open(configFilePath).read()
config = json.loads(json_text)

path= config['path']['root']+config['path']['focus']

# setup log file
pathFileNameLog = config['path']['root']+config['path']['log']+'/focus.log'
print(f"Focus process, logpath = {pathFileNameLog}")
logging.basicConfig(filename=pathFileNameLog,level=logging.WARNING,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
# create and connect to Camera 
camSpectro=CamSpectro(config["ccdSpectro"])
#camSpectro.setBinning({'X':1,'Y':1})

#acquisition
exposureTime = 5
focusAmplitude=2000
focusNbPoint=8

focusOrigin = astrosib.get_focus()
print(f"Original focus Position = {focusOrigin}")
focusStart = int(focusOrigin-focusAmplitude/2)
focusStop  = int(focusOrigin+focusAmplitude/2)

focusPosRange = range(focusStart,focusStop,focusAmplitude//(focusNbPoint-1))
print(f"We will test the following focus position: {list(focusPosRange)}")
focusMeans = []

plt.ion()
plt.show()

fig, (ax1, ax2) = plt.subplots(2,sharex=True)
fig.suptitle('preview spectrum')
ax1.set_title("2D image")
ax2.set_title("binned profil")
ax2.set_xlabel("pixel X coord")


for focusPos in focusPosRange:
    print(f"go to focus position {focusPos}")
    astrosib.set_focus_abs(focusPos)

    print("run acquisition")
    camSpectro.newAcquSerie(path,"FOCUS-",1,exposureTime)
    camSpectro.waitEndAcqSerie()
    print("acquisition finished")

    # stat
    filename = path+"/FOCUS-1.fits"

    stat = statSpectrum(filename,binnigHeight = 60)

    print(f"Mean = {stat['mean']} Max = {stat['max']}")
    focusMeans.append(stat['mean'])

    ax1.imshow(stat['img'], cmap=plt.cm.gray) 
    ax2.plot(stat['spectrum'],label=f"foc {focusPos} step")
    ax2.legend(loc='upper right')
    plt.draw()
    plt.pause(0.1)

print(f"go back to orginal focus Position = {focusOrigin}")
astrosib.set_focus_abs(focusOrigin)

plt.close()


print(f"FocusRange:  {list(focusPosRange)}")
print(f"means {focusMeans}")

plt.ioff()
plt.plot(list(focusPosRange),focusMeans)
plt.title("Means vs focus position")
plt.show()

