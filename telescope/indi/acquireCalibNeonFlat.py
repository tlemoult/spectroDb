import os,sys,time, datetime,logging,json
import PyIndi

from libindi.camera import CameraClient as CamSpectro

n=len(sys.argv)

if n!=2:
    print("syntaxe:")
    print('    python3 acquireCalibNeonFlat.py configAcquire.json')
    exit()


#load configuration
json_text=open(sys.argv[1]).read()
config=json.loads(json_text)
# setup log file
logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

#create directory
basePath=config['path']['root']+'/'+config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').replace(':','-').split('.')[0]
basePath+='-'+"NeonFlat"
print(f"basePath={basePath}")
os.mkdir(basePath)


# instantiate the client, for camera

camSpectro=CamSpectro(config["ccdSpectro"])

print("neon acquisition" )
input('Switch on the NEON lamp, Press enter to continue: ')

spectroCalib=config['spectro']['ALPY']['calib']
camSpectro.newAcquSerie(basePath,"neon-",spectroCalib['nbExpo'],spectroCalib['exposure'])
camSpectro.waitEndAcqSerie()
print("  acquisition finished")
input('Switch off NEON lamp, Press enter to continue: ')

print("flat Acquisition" )
input('Switch on the flat lamp, Press enter to continue: ')

spectroFlat=config['spectro']['ALPY']['flat']
camSpectro.newAcquSerie(basePath,"flat-",spectroFlat['nbExpo'],spectroFlat['exposure'])
camSpectro.waitEndAcqSerie()
print("  acquisition finished")
input('Switch off Flat lamp, Press enter to continue: ')

print("acquisition finished")

camSpectro.disconnectServer()

time.sleep(2)
