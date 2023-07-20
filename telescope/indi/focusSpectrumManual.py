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
logging.basicConfig(filename=pathFileNameLog,level=logging.WARNING,format='%(asctime)s %(message)s')
# create and connect to Camera 
camSpectro=CamSpectro(config["ccdSpectro"])
#camSpectro.setBinning({'X':1,'Y':1})

#acquisition
exposureTime = 5

plt.ion()
plt.show()

fig, (ax1, ax2) = plt.subplots(2,sharex=True,figsize=(13, 7))
fig.suptitle('preview spectrum')
ax1.set_title("2D image")
ax2.set_title("binned profil")
ax2.set_xlabel("pixel X coord")

focusPos = 0
focusMeans = []
user_response=''
while user_response == '':
    
    focusPos += 1
    print(f"run acquisition no {focusPos}")
    camSpectro.newAcquSerie(path,"FOCUS-",1,exposureTime)
    camSpectro.waitEndAcqSerie()
    print("acquisition finished")

    # stat
    filename = path+"/FOCUS-1.fits"

    stat = statSpectrum(filename,binnigHeight = 60)

    print(f"Mean = {stat['mean']} Max = {stat['max']}")
    focusMeans.append(stat['mean'])

    ax1.imshow(stat['img'], cmap=plt.cm.gray) 
    ax2.plot(stat['spectrum'],label=f"foc {focusPos} iteration")
    ax2.legend(loc='upper right')
    plt.draw()
    plt.pause(0.1)

    user_response = input("Enter press S to stopEnter")


plt.close()

print(f"range {range(focusPos)}")
print(f"means {focusMeans}")

plt.ioff()
plt.plot(range(1,focusPos+1),focusMeans)
plt.title("Spectrum Flux vs focus Index")
plt.show()

