import os,sys,time, datetime,logging,json
import PyIndi

from libindi.camera import CameraClient as CamSpectro
import libobs.powerControl as powerControl

n=len(sys.argv)
if n==1:
    print("usage: arguments\n  neon   => acquire neon\n  flat   => acquire flat\n  camera => acquire offset and dark")
    exit()
else:
    if sys.argv[1]=='flat':
        mode_flat_acquire = True
    elif sys.argv[1]=='camera':
        mode_flat_acquire = False

#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
json_text=open(configFilePath).read()
config = json.loads(json_text)
CalibManual = True

# setup log file
logFilePath = config['path']['root']+config['path']['log']+'/'+config['logFile']
print(f"{logFilePath=}")
logging.basicConfig(filename=logFilePath,level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

#create directory
basePath=config['path']['root']+'/'+config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').replace(':','-').split('.')[0]
basePath+='-'+"calibCCD"
print(f"basePath={basePath}")
os.mkdir(basePath)

# instantiate the client, for camera
camSpectro=CamSpectro(config["ccdSpectro"])
spectroName = config['spectro']['selected']
print(f"{spectroName=}")
print(f"run calibration {sys.argv[1:]} with camera {config['ccdSpectro']['name']}" )

if 'neon' in sys.argv:
    print('Switch on the NEON lamp')
    relay_calib_neon = 5
    if CalibManual:
        input("press Enter when done")
    else:
        powerControl.set(relay_calib_neon,True)
    for spectroCalib in config['spectro'][spectroName]['calib']:
        camSpectro.newAcquSerie(basePath,spectroCalib['serieName'],spectroCalib['nbExpo'],spectroCalib['exposure'])
        camSpectro.waitEndAcqSerie()
    print("acquisition finished")
    if CalibManual:
        input("press Enter when done")
    else:
        powerControl.set(relay_calib_neon,False)

if 'flat' in sys.argv:
    print("flat Acquisition" )
    print('Switch on the FLAT lamp')
    relay_flat_lamp = 6
    if CalibManual:
        input("press Enter when done")
    else:
        powerControl.set(relay_flat_lamp,True)

    for spectroFlat in config['spectro'][spectroName]['flat']:
        camSpectro.newAcquSerie(basePath,spectroFlat['serieName'],spectroFlat['nbExpo'],spectroFlat['exposure'])
        camSpectro.waitEndAcqSerie()
    print("  acquisition finished")

    print('Switch off the Flat lamp')
    if CalibManual:
        input("press Enter when done")
    else:
        powerControl.set(relay_flat_lamp,True)

if 'camera' in sys.argv:

    input('Put camera in the dark condition...., Press enter to continue: ')

    print("Offset Acquisition" )
    for offsetConfig in config["ccdSpectro"]['offset']:
        camSpectro.newAcquSerie(basePath,offsetConfig['serieName'],offsetConfig['nbExpo'],offsetConfig['exposure'])
        camSpectro.waitEndAcqSerie()
    print("  acquisition finished")


    print("Dark Acquisition")
    for darkConfig in config["ccdSpectro"]['dark']:
        camSpectro.newAcquSerie(basePath,darkConfig['serieName'],darkConfig['nbExpo'],darkConfig['exposure'])
        camSpectro.waitEndAcqSerie()


print("acquisition finished")


camSpectro.disconnectServer()

time.sleep(2)
