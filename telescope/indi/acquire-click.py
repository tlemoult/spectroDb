import os,sys,time, datetime,logging,json,click
import PyIndi

from lib.CamSpectro import IndiClient as CamSpectro

@click.command()
@click.option('--proj', default='none', help='Project Name, like Bess, NewBe')
@click.option('--typ', default='obj', type=click.Choice(['obj', 'ref']), help='Define target is science or a reference')
@click.option('--name', help='name , must be readable by CDS')
@click.option('--qty', default=1,  help='exposure frame quantities')
@click.option('--duration', default=1,type=float, help='exposure time for each frame')

def acquire(proj,typ,name,qty,duration):
    
    if name==None:
        print "name is mandatory"
        exit()
    print "projectName=",proj
    print "objType=",typ
    print "objName=",name
    print "nbExposure=",qty
    print "expTime=",duration

    #load configuration
    json_text=open('./configAcquire.json').read()
    config=json.loads(json_text)
    # setup log file
    logging.basicConfig(filename=config['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

    #create directory
    basePath=config['path']['acquire']+'/'+str(datetime.datetime.now()).replace(' ','_').split('.')[0]
    basePath+='-'+name.replace(' ','_').replace('+','p').replace('*','s')
    print "basePath=",basePath
    os.mkdir(basePath)

    #create observation.json
    observationJson=config['templateObservation']
    observationJson['target']['objname']=[name]
    observationJson['target']['isRef']=(typ=='ref')
    observationJson['project']=proj
    observationJson['target']['coord']['ra']=""
    observationJson['target']['coord']['dec']=""
    observationJson['statusObs']="started"
    observationJson['obsConfig']['NbExposure']=qty
    observationJson['obsConfig']['ExposureTime']=duration
    observationJson['obsConfig']['TotalExposure']=qty*duration

    with open(basePath+'/observation.json', 'w') as outfile:
        json.dump(observationJson, outfile)

    # instantiate the client, for camera
    camSpectro=CamSpectro(config['ccdSpectro']['name'])
    # set indi server
    server=config['ccdSpectro']['server']
    camSpectro.setServer(str(server['host']),server['port'])
    # connect to indi server
    print("Connecting and waiting 2secs")
    if (not(camSpectro.connectServer())):
        print("No indiserver running on "+camSpectro.getHost()+":"+str(camSpectro.getPort())+" - Try to run")
        print("  indiserver indi_simulator_ccd")
        sys.exit(1)
    time.sleep(2)

    #acquisition
    print "run acquisition" 
    camSpectro.newAcquSerie(basePath,"OBJECT-",nbExposure,expTime)
    camSpectro.waitEndAcqSerie()

    raw_input('Switch on Neon, Press enter to continue: ')
    camSpectro.newAcquSerie(basePath,"NEON-",1,5)
    camSpectro.waitEndAcqSerie()

    #update json file
    observationJson['obsConfig']['NbExposure']=nbExposure
    observationJson['obsConfig']['ExposureTime']=expTime
    observationJson['obsConfig']['TotalExposure']=nbExposure*expTime
    observationJson['statusObs']="finished"
    with open(basePath+'/observation.json', 'w') as outfile:
        json.dump(observationJson, outfile)

    print("acquisition finished")

    raw_input('Switch off Neon, Press enter to continue: ')


if __name__ == '__main__':
    acquire()
