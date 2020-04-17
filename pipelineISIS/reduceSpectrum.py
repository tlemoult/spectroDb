import os,time,json,shutil
from datetime import datetime

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
            continue
        
        if f.startswith('_'):
            interrestingFileList.append(f)
            continue

        if f.startswith('observation.json'):
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


#signal path
signalPipeline=racineArchive+path['signalProcessPipe']
PathSignalStartPipeline=signalPipeline+"/askStart"
PathSignalEndedPipeline=signalPipeline+"/ended"

#source raw path
PathPipelineSrcRaw=path['eShelPipe']+'/raw'
PathPipelineSrcCalib=path['eShelPipe']+'/calib'

#destination path
eShelPipeProcessedRoot=path['eShelPipe']+'/processed'

#work path
eShelPipeFastWork=path['eShelPipeFastWork']+'/work'
PathObservationJson=eShelPipeFastWork+'/observation.json'
PathObjectFileName=eShelPipeFastWork+"/objname.txt"


cmdStartPipeline="actionna.bat"
loopSleepTime=1

while True:

    print("Wait start signal ",PathSignalStartPipeline)
    while not os.path.isfile(PathSignalStartPipeline):
        time.sleep(loopSleepTime)

    print("Received start signal",PathSignalStartPipeline)
    os.remove(PathSignalStartPipeline)

    #dst path
    now = datetime.now()
    strDate= now.strftime("%Y-%m-%d-%H-%M-%S")
    eShelPipeProcessed=eShelPipeProcessedRoot+'/'+strDate
    print("create traget processed directory",eShelPipeProcessed)
    os.mkdir(eShelPipeProcessed)

    print("clean directory eShelPipeFastWork=",eShelPipeFastWork)
    for f in os.listdir(eShelPipeFastWork):
        p=eShelPipeFastWork+'/'+f
        if os.path.isfile(p):
            #print("file", f)
            os.remove(p)
        if os.path.isdir(p):
            #print("dir",f)
            shutil.rmtree(p)

    print("copy calibration files directory from",PathPipelineSrcCalib,"to",eShelPipeFastWork)
    shutil.copytree(PathPipelineSrcCalib,eShelPipeFastWork+'/calib')

    print("move raw files from",PathPipelineSrcRaw,"to",eShelPipeFastWork)
    for f in os.listdir(PathPipelineSrcRaw):
        src=PathPipelineSrcRaw+'/'+f
        dst=eShelPipeFastWork+'/'+f
        print("     move file",src,"-to->",dst)
        shutil.move(src,dst)

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
    renameCalib(eShelPipeFastWork,"TUNGSTEN","tung","calib")
    renameCalib(eShelPipeFastWork,"CALIB","thor","calib")
    renameCalib(eShelPipeFastWork,"LED","led","calib")

    print("Start ISIS pipeline")
    os.system(cmdStartPipeline)

    archiveProcessedFiles(eShelPipeFastWork,eShelPipeProcessed)

    print("END of ISIS pipeline")
    f = open(PathSignalEndedPipeline,"w")
    f.write("ISIS end")
    f.close()
