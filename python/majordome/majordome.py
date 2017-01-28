import os,time,json

json_text=open("../config/config.json").read()
config=json.loads(json_text)
path=config['path']

racineArchive=path['archive']
signalPrism=path['signalPrism']
PathFileNewRaw=racineArchive+signalPrism+"/newRawData"
cmdSignalNewRaw="../tools/in-raw-run.sh"

print "Majordome, check every 60 seconds."
print "  Signals: "+PathFileNewRaw+"   => action="+cmdSignalNewRaw

while True:
	print ".",
	if os.path.isfile(PathFileNewRaw):
		os.system(cmdSignalNewRaw)
		os.remove(PathFileNewRaw)

	time.sleep(60)
