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
        except IOError, message:
            #print "File is locked (unable to open in append mode). %s." % message
            locked = True
        finally:
            if file_object:
                file_object.close()
                #print "%s closed." % filepath
    else:
        print "%s not found." % filepath
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
signalAudela=path['signalAudela']
PathSignalStartPipeline=racineArchive+signalAudela+"/eShelPipeLine-askStart"
PathSignalEndedPipeline=racineArchive+signalAudela+"/eShelPipeLine-end"

cmdInNewRaw="../tools/in-raw-run.sh"
cmdInNewProcessed="../tools/in-processed-run.sh"

print "Majordome, check every 60 seconds."
print "Check  Signals: "+PathSignalNewRaw
print "   => action="+cmdInNewRaw+""
print "   => action trigger signal"+PathSignalStartPipeline
print
print "  Signals: "+PathSignalEndedPipeline
print "   => action="+cmdInNewProcessed


MinDurationEndProcessEshel=60
timerEndProcessEshel=0
while True:

	#########  start raw integration,  then  start spectrum reduction.
	if os.path.isfile(PathSignalNewRaw):
		print "Raw receive from Telescope"
		print "start Raw integration in archive"
		os.system(cmdInNewRaw)
		os.remove(PathSignalNewRaw)
		print "End of Raw integration in archive"
		print "Trigger spectral reduction pipeline"
		open(PathSignalStartPipeline, 'a').close()  # declenche la reduction pipeline audela

	#######  check if eShel Pipeline is stopped  #####
	if isEndProcessEshel(PathProcessedFiles,PathTmpPipeFiles):
		timerEndProcessEshel+=1
	else:
		timerEndProcessEshel=0

	if timerEndProcessEshel>=MinDurationEndProcessEshel:
		timerEndProcessEshel=MinDurationEndProcessEshel   # avoid overflow
		isEndProcessEshelOnDuration=True
	else:
		isEndProcessEshelOnDuration=False

	######## start integration of processed spectrum
	if len(os.listdir(PathProcessedFiles))!=0 and isEndProcessEshelOnDuration:
		print "new processed files and no processing in progress"
		print "start spectrum integration in archive"
		os.system(cmdInNewProcessed)          # on integre en base les nouveaux spectres
		print "End of spectrum integration in archive"

	# attente bloucle
	time.sleep(1)
