import sys
import libsdb.defineTimeSerie as defineTimeSerie

configPathFile="../../config/config.json"

print("redefinie les time serie facon Audela")

if len(sys.argv)<3:
	print("nombre d'argument incorrect")
	print("utiliser: ")
	print("    python3 defineTimeSerie.py ObsId NbRawPerStack")
	print("ou  python3 defineTimeSerie.py range obsIdStart obsIdStop NbRawPerStack")
	exit(1)

if len(sys.argv)==3:
	obsIds=[int(sys.argv[1])]
	NbRawPerStack=int(sys.argv[2])
	defineTimeSerie.redefineTimeSerieObject(obsIds,NbRawPerStack,configPathFile)
elif len(sys.argv)==5 and sys.argv[1]=='range':
	obsIds=list(range(int(sys.argv[2]),int(sys.argv[3])+1))
	NbRawPerStack=int(sys.argv[4])
	defineTimeSerie.redefineTimeSerieObject(obsIds,NbRawPerStack,configPathFile)
else:
	print("arguments incorrects")
	exit()
