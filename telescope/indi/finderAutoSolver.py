import lib.solveAstro as solver
import subprocess,os
import json,time

def doFinderSolveAstro(config):
	### Picture acquisition with Finder Scope
	fileNameImage=config["path"]["image"]
	#todo: replace this  C compiled INDI client by pure python with PyIndi lib.
	callAquisitionArray =  ["./cameraClient/myClient", config["camera"]["indiServerAddress"], \
					str(config["camera"]["indiServerPort"]), \
					config["camera"]["name"], \
					str(config["acquisition"]["binning"]), str(config["acquisition"]["binning"]), \
					str(config["acquisition"]["exposureTime"]), fileNameImage]
	subprocess.call(callAquisitionArray)

	### Plate Solving
	fenteXpix=config["centerX"]
	fenteYpix=config["centerY"]
	scaleArcPerPixelFinder=config["scale"]
	try:
		w=solver.solveAstro(fileNameImage,scaleArcPerPixelFinder)
		wx, wy = w.wcs_pix2world(fenteXpix, fenteYpix,1)
	except:
		print("error during plate solving...")
		wx, wy = "error","error"
	
	### Store & Display Result
	print("fente X=",fenteXpix," ,Y=",fenteYpix)
	print('RA={0}deg  DEC={1}deg '.format(wx, wy))

	f = open(config["path"]["output"], "w")
	f.write("#format:  RA in degree, then DEC in degree\n")
	f.write(f"{wx}\n")
	f.write(f"{wy}\n")
	f.close()

print(f"This is a automatic finder solver by plate solving")

config=json.loads(open('./configAutoSolver.json').read())

### clean signals and outputs
try:
	os.remove(config["path"]["signalEnd"])
	os.remove(config["path"]["signalStart"])
	os.remove(config["path"]["output"])
except:
	print("    Some file was not here.")

print(f'Wait for file {config["path"]["signalStart"]}')

while True:
	if os.path.isfile(config["path"]["signalStart"]):
		try:
			os.remove(config["path"]["signalStart"])
		except:
			print(f'   file {config["path"]["signalStart"]} cannot be deleted...')
		doFinderSolveAstro(config)
		print(f'Wait for file {config["path"]["signalStart"]}')
	
	# attente bloucle
	time.sleep(1)

