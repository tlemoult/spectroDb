import os,time,json

def is_locked(filepath):
    """Checks if a file is locked by opening it in append mode.
    If no exception thrown, then the file is not locked.
    """
    locked = None
    file_object = None
    if os.path.exists(filepath):
        try:
            #print "Trying to open %s." % filepath
            buffer_size = 8
            # Opening file in append mode and read the first 8 characters.
            file_object = open(filepath, 'a', buffer_size)
            if file_object:
                #print "%s is not locked." % filepath
                locked = False
        except IOError as message:
            #print "File is locked (unable to open in append mode). %s." % message
            locked = True
        finally:
            if file_object:
                file_object.close()
                #print "%s closed." % filepath
    else:
        print("%s not found." % filepath)
    return locked

def isEndProcessEshel(PathProcessedFiles,PathTmpPipeFiles):

	if len(os.listdir(PathTmpPipeFiles))==2:
		tmpDirClean=True
	else:
		tmpDirClean=False
		#print "Tmp dir is not clean"

	isLockedProcessFiles=False
	for file in os.listdir(PathProcessedFiles):
		if is_locked(PathProcessedFiles+'/'+file):
			openProcessFiles=True
			#print "file:"+file+" is locked"

	return tmpDirClean and (not isLockedProcessFiles)

json_text=open("../config/config.json").read()
config=json.loads(json_text)
path=config['path']

racineArchive=path['archive']
signalPrism=path['signalPrism']
PathProcessedFiles=path['eShelPipe']+'/processed'
PathTmpPipeFiles=path['eShelPipe']+'/temp'
PathSignalNewRaw=racineArchive+signalPrism+"/newRawData"
signalPipeline=path['signalProcessPipe']
PathSignalStartPipeline=racineArchive+signalPipeline+"/askStart"
PathSignalEndedPipeline=racineArchive+signalPipeline+"/ended"

cmdInNewRaw="../base/in-raw-run.sh"
cmdInNewProcessed="../base/in-processed-run.sh"

print("Majordome, check every 60 seconds.")
print("Check  Signals: "+PathSignalNewRaw)
print("   => action="+cmdInNewRaw+"")
print("   => action trigger signal"+PathSignalStartPipeline)
print()
print("  Signals: "+PathSignalEndedPipeline)
print("   => action="+cmdInNewProcessed)


while True:

	#########  start raw integration,  then  start spectrum reduction.
	if os.path.isfile(PathSignalNewRaw):
		print("Raw receive from Telescope")
		print("start Raw integration in archive")
		os.system(cmdInNewRaw)
		os.remove(PathSignalNewRaw)
		print("End of Raw integration in archive")

	# attente bloucle
	time.sleep(1)
