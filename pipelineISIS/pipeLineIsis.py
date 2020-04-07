import os,time,json

def renameCalib(path,prefix,newprefix,gen):
    for filename in os.listdir(path):
        if filename.startswith(prefix):
            src=path+'/'+filename
            dst=path+'/'+gen+'_'+filename.replace(prefix,newprefix)
            print(f"rename src:{src}   dst:{dst}")
            os.rename(src,dst)

#open local configuration file
json_text=open("./config.json").read()
config=json.loads(json_text)
path=config['path']
racineArchive=path['archive']

PathPipeline=racineArchive+path['pipeline']
signalPipeline=racineArchive+path['signalsPipe']
PathSignalStartPipeline=signalPipeline+"/eShelPipeLine-askStart"
PathSignalEndedPipeline=signalPipeline+"/eShelPipeLine-end"

PathObservationJson=PathPipeline+'/observation.json'
PathObjectFileName=PathPipeline+"/objname.txt"
cmdStartPipeline="go-process.bat"
loopSleepTime=1


while True:
    time.sleep(loopSleepTime)

    if not os.path.isfile(PathSignalStartPipeline):
        continue

    print("Received start signal",PathSignalStartPipeline)
#    os.remove(PathSignalStartPipeline)

    if not os.path.isfile(PathObservationJson):
        print("Error cannot found Json "+PathObservationJson)
        continue
    jsonObs=open(PathObservationJson).read()
    configObs=json.loads(jsonObs)

    objname=configObs['target']['objname'][0]
    print("Generate object filename",PathObjectFileName,'with name "'+objname+'"')
    f = open(PathObjectFileName,"w")
    f.write(objname)
    f.close()

    print("rename calibration files")
    renameCalib(PathPipeline,"TUNGSTEN","tung","calib")
    renameCalib(PathPipeline,"CALIB","thor","calib")
    renameCalib(PathPipeline,"LED","led","calib")

    print("Start ISIS pipeline")
    os.system(cmdStartPipeline)

    print("END of ISIS pipeline")
    f = open(PathSignalEndedPipeline,"w")
    f.write("ISIS end")
    f.close()

    exit()
