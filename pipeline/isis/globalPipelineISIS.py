

import os,json,sys,time,shutil
from datetime import datetime

def renameCalib(path,prefix,newprefix,gen):
    for filename in os.listdir(path):
        if filename.startswith(prefix):
            src=path+'/'+filename
            dst=path+'/'+gen+'_'+filename.replace(prefix,newprefix)
            #print(f"rename src:{src}   dst:{dst}")
            os.rename(src,dst)

def archiveProcessedFiles(src,dst):
    print("archiveProcessedFiles src"+src+"  dst="+dst)

    print("  copy calibration directory")
    shutil.rmtree(dst+"/calib",ignore_errors=True)
    shutil.copytree(src+"/calib",dst+"/calib")

    fileList=os.listdir(src)
    interrestingFileList=[]

    series=False
    for f in fileList:
        if f.startswith("@pro") :
            interrestingFileList.append(f)
            series=True
    print("series="+str(series))

    for f in fileList:
        if f.endswith('.xml') or f.endswith('.log') or f.startswith('observation.json'):
            interrestingFileList.append(f)
            continue
        
        if (not series) and f.startswith('_'):  # we exclude cummulated exposure, if we have a serie.
            interrestingFileList.append(f)
            continue

    print("  copy InterrestedFile\n  ")
    for f in interrestingFileList:
        print("    copy ",f)
        shutil.copy(src+'/'+f,dst+'/'+f)

def convertJSONtoINI(sourcePath,destinationPath):
    print("load Json ",sourcePath)
    jsonObs=open(PathObservationJson).read()
    jsonTable=json.loads(jsonObs)
    objname=jsonTable['target']['objname'][0]
    try:
        series=jsonTable['obsConfig']['Series']
    except:
        #default value, if not defined in JSON file
        series='false'

    print("Generate ini parameters filename",destinationPath,'object name = "'+objname+'"  series = '+series)
    f = open(destinationPath,"w")
    f.write("objname="+objname+"\n")
    f.write("series="+series+"\n")
    f.close()

if len(sys.argv)<2:
	print("nombre d'argument incorrect")
	print("utiliser: ")
	print("   python globalPipelineISIS.py obsId1 obsId2 ...")
	print("   python globalPipelineISIS.py range obsIdStart obsIdStop ")
	exit(1)


print("load configuration")
json_text=open("../../config/config.json").read()
config=json.loads(json_text)
path=config['path']
racineArchive=path['archive']

#source Calib path
PathPipelineSrcCalib=path['eShelPipeFastWork']+'/calib'

#destination path for processed
eShelPipeProcessedRoot=path['eShelPipeFastWork']+'/processed'

#work path
eShelPipeFastWork=path['eShelPipeFastWork']+'/work'
PathObservationJson=eShelPipeFastWork+'/observation.json'
PathObservationINI=eShelPipeFastWork+"/observation.ini"



loopSleepTime=1

print("process command line argument")
if len(sys.argv)==2:
	obsIds=[int(sys.argv[1])]
else:
	if sys.argv[1]=='range':
		obsIds=range(int(sys.argv[2]),int(sys.argv[3])+1)
	else:
		obsIds=[]
		for arg in sys.argv[1:]:
				obsIds.append(int(arg))

print("Selected ObsId=",obsIds)
print("************")

print("start loop process observations")
for obsId in obsIds:
    print("***observation ID = ",obsId)

    #dst path
    now = datetime.now()
    strDate= now.strftime("%Y-%m-%d-%H-%M-%S")
    eShelPipeProcessed=eShelPipeProcessedRoot+'/'+strDate
    print("create target processed directory",eShelPipeProcessed)
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

    orgPath=os.getcwd()
    os.chdir("..")
    print("Fill observation RAW Calib files")
    os.system("python fillObservationRawCalib.py "+str(obsId))

    print("Get Raw spectrum")
    os.chdir("../base")
    os.system("python get-raw-obs.py"+" "+str(obsId)+" "+eShelPipeFastWork)
    os.chdir(orgPath)

    print("copy calibration files directory from",PathPipelineSrcCalib,"to",eShelPipeFastWork)
    shutil.copytree(PathPipelineSrcCalib,eShelPipeFastWork+'/calib')

    if not os.path.isfile(PathObservationJson):
        print("Error cannot found Json "+PathObservationJson)
        continue
    convertJSONtoINI(PathObservationJson,PathObservationINI)

    print("rename calibration files")
    renameCalib(eShelPipeFastWork,"TUNGSTEN","tung","calib")
    renameCalib(eShelPipeFastWork,"CALIB","thor","calib")
    renameCalib(eShelPipeFastWork,"LED","led","calib")

    print("Start ISIS pipeline")
    os.system("actionna.bat")

    archiveProcessedFiles(eShelPipeFastWork,eShelPipeProcessed)

    print("END of ISIS pipeline")

    print("**** Integrate processed spectrum in data base")

    now = datetime.now()
    strDate = now.strftime("%Y-%m-%d-%H-%M-%S")
    logFile = racineArchive+"/log/in.processed."+strDate+".log"
    errFile = racineArchive+"/log/in.processed."+strDate+".err"
    cmdProcess="python in-processed.py "+eShelPipeProcessedRoot+" >"+logFile+" 2> "+errFile
    orgPath=os.getcwd()
    os.chdir('../../base')
    print(cmdProcess)
    os.system(cmdProcess)
    os.chdir(orgPath)

    print("delete iSIS work files")
    shutil.rmtree(eShelPipeProcessed)


