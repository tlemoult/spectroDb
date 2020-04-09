import os,time,json,shutil

def renameCalib(path,prefix,newprefix,gen):
    for filename in os.listdir(path):
        if filename.startswith(prefix):
            src=path+'/'+filename
            dst=path+'/'+gen+'_'+filename.replace(prefix,newprefix)
            #print(f"rename src:{src}   dst:{dst}")
            os.rename(src,dst)

def archiveProcessedFiles(src,dst):
    print(f"archiveProcessedFiles src={src}  dst={dst}")

    print("  copy calibration directory")
    shutil.rmtree(dst+"/calib",ignore_errors=True)
    shutil.copytree(src+"/calib",dst+"/calib")

    interrestingFileList=[]
    for f in os.listdir(src):
        if f.endswith('.xml') or f.endswith('.log'):
            interrestingFileList.append(f)
            continue

        if f.startswith("@pro") :
            interrestingFileList.append(f)
        
        if f.startswith('_'):
            interrestingFileList.append(f)
            continue

    print("  copy InterrestedFile\n  ")
    for f in interrestingFileList:
        print("    copy ",f)
        shutil.copy(src+'/'+f,dst+'/'+f)


#open local configuration file
json_text=open("../python/config/config.json").read()
config=json.loads(json_text)
path=config['path']
racineArchive=path['archive']

PathPipeline=path['eShelPipe']
signalPipeline=racineArchive+path['signalProcessPipe']
PathSignalStartPipeline=signalPipeline+"/askStart"
PathSignalEndedPipeline=signalPipeline+"/ended"

PathObservationJson=PathPipeline+'/observation.json'
PathObjectFileName=PathPipeline+"/objname.txt"
cmdStartPipeline="go-process.bat"
loopSleepTime=1

while True:

    print("Wait start signal ",PathSignalStartPipeline)
    while not os.path.isfile(PathSignalStartPipeline):
        time.sleep(loopSleepTime)

    print("Received start signal",PathSignalStartPipeline)
#    os.remove(PathSignalStartPipeline)

    print("load Json ",PathObservationJson)
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
    renameCalib(PathPipelineWork,"TUNGSTEN","tung","calib")
    renameCalib(PathPipelineWork,"CALIB","thor","calib")
    renameCalib(PathPipelineWork,"LED","led","calib")

    print("Start ISIS pipeline")
    os.system(cmdStartPipeline)

    print("END of ISIS pipeline")
    f = open(PathSignalEndedPipeline,"w")
    f.write("ISIS end")
    f.close()
