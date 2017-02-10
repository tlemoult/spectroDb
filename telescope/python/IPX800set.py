import sys
import urllib

if ( len(sys.argv)==1):
	print "exemple"
	print "python IPX800set.py 4=1"
	print "pour activer le relais 4"
	exit()
	
argno=sys.argv[1]
urlname="http://192.168.0.10/preset.htm?set"+argno
response = urllib.urlopen(urlname)
data=response.read()
	
