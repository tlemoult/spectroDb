

import os,json,sys,time


#####################
#delete previous processed file
#get raw
#trigger pipeline
#in processed


if len(sys.argv)<2:
	print("nombre d'argument incorrect")
	print("utiliser: ")
	print("   python process-spectrum.py obsId1 obsId2 ...")
	print("   python process-spectrum.py range obsIdStart obsIdStop ")
	exit(1)


print("load configuration")
json_text=open("../config/config.json").read()
config=json.loads(json_text)
path=config['path']
racineArchive=path['archive']
signalPipeline=path['signalProcessPipe']
PathSignalStartPipeline=racineArchive+signalPipeline+"/askStart"
PathSignalEndedPipeline=racineArchive+signalPipeline+"/ended"
PatheShelPipeRaw=path['eShelPipe']+'/raw'

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

if os.path.isfile(PathSignalEndedPipeline):
	print("Clean obsolete end signal "+PathSignalEndedPipeline)
	os.remove(PathSignalEndedPipeline)

print("process spectrum ")
for obsId in obsIds:
	print("***observationID=",obsId)
	print("Clean raw dir "+PatheShelPipeRaw)
	for f in os.listdir(PatheShelPipeRaw):
		p=PatheShelPipeRaw+'/'+f
		if os.path.isfile(p):
			os.remove(p)

	os.system("python ../tools/get-raw-obs.py"+" "+str(obsId))

	print("**** Send start pipeline signal")
	open(PathSignalStartPipeline,"w").close()

	print("**** Wait end pipeline signal")
	while not os.path.isfile(PathSignalEndedPipeline):
		time.sleep(1)
	os.remove(PathSignalEndedPipeline)

print("**** Integrate processed spectrum in data base")
os.system("../tools/in-processed-run.sh")



