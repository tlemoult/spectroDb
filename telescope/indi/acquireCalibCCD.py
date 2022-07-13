import os,sys,time, datetime,logging,json
import PyIndi

from myLib.camera import CameraClient as CamSpectro

n=len(sys.argv)

if n!=2:
    print("syntaxe:")
    print('    python3 acquireCalibCCD.py configAcquire.json')
    exit()


#load configuration
json_text=open(sys.argv[1]).read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

#create directory
basePath=config['path']['root']+'/'+config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').replace(':','-').split('.')[0]
basePath+='-'+"calibCCD"
print(f"basePath={basePath}")
os.mkdir(basePath)


# instantiate the client, for camera

camSpectro=CamSpectro(config["ccdSpectro"])

print("flat Acquisition" )
input('Switch on the flat lamp, Press enter to continue: ')

camSpectro.newAcquSerie(basePath,"flat-",21,4)
camSpectro.waitEndAcqSerie()
print("  acquisition finished")
input('Switch off Flat lamp, Press enter to continue: ')
input('Put camera in the dark condition...., Press enter to continue: ')


print("Offset Acquisition" )
camSpectro.newAcquSerie(basePath,"offset-",15,0.1)
camSpectro.waitEndAcqSerie()
print("  acquisition finished")


print("Dark Acquisition")
camSpectro.newAcquSerie(basePath,"dark-",7,300)
camSpectro.waitEndAcqSerie()


print("acquisition finished")


camSpectro.disconnectServer()

time.sleep(2)
