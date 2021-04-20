import solveAstro as solver
import subprocess,os
import json,time

def writeStatus(config,status):
	f = open(config['path']['signalStatus'],"w")
	f.write(status)
	f.close()
	
def cleanStartFile(config):
	try:
		os.remove(config["path"]["signalStart"])
		os.remove(config["path"]["output"])
	except:
		print("    Some files, cannot be deleted.")

def doFinderSolveAstro(config):
	### Picture acquisition with Finder Scope
	if config['testWithoutSky']:
		fileNameImage=config["imageTest"]
		print(f"Test without sky, use {fileNameImage}",fileNameImage)
		time.sleep(2)
	else:
		fileNameImage=config["path"]["image"]
		#todo: replace this  C compiled INDI client by pure python with PyIndi lib.
		aquisitionCmdLine =  [config["path"]["camClientExe"],\
						config["camera"]["indiServerAddress"], \
						str(config["camera"]["indiServerPort"]), \
						config["camera"]["name"], \
						str(config["acquisition"]["binning"]), str(config["acquisition"]["binning"]), \
						str(config["acquisition"]["exposureTime"]),\
						fileNameImage]
		subprocess.call(aquisitionCmdLine)

	### Plate Solving
	fenteXpix=config["centerX"]
	fenteYpix=config["centerY"]
	scaleArcPerPixelFinder=config["scale"]
	try:
		w=solver.solveAstro(fileNameImage,scaleArcPerPixelFinder)
		wx, wy = w.wcs_pix2world(fenteXpix, fenteYpix,1)
		resultStatus = "Success"
	except:
		print("error during plate solving...")
		resultStatus = "Error"
		return resultStatus
	
	### Store & Display Result
	print("fente X=",fenteXpix," ,Y=",fenteYpix)
	print('RA={0}deg  DEC={1}deg '.format(wx, wy))

	pi = 3.141592653589793
	f = open(config["path"]["output"], "w")
	f.write("#format:  RA, then DEC in radian\n")
	f.write(f"{wx/180.0*pi}\n")
	f.write(f"{wy/180.0*pi}\n")
	f.close()

	result= { "protoVersion":"1.00", "status":resultStatus, "coordRADIAN": {"RA": wx/180.0*pi, "DEC":wy/180.0*pi }}

	return result

print(f"This is a automatic finder solver by plate solving")

config=json.loads(open('./configAutoSolver.json').read())
cleanStartFile(config)

print(f'Wait for file {config["path"]["signalStart"]}')

while True:
	if not os.path.isfile(config["path"]["signalStart"]):
		continue

	cleanStartFile(config)
	writeStatus(config,"started")
	writeStatus(config,doFinderSolveAstro(config)["status"])
	print(f'Wait again for file {config["path"]["signalStart"]}')
	
	# attente bloucle
	time.sleep(1)

