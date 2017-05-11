#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import serial
import sys
import urllib

print "Passage d une commande au telescope astrosib"

nbArgs=len(sys.argv)
if nbArgs==1:
	print "Syntaxe:"
	print "  python astrosib-cmd.py COM9 SHUTTEROPEN?1,1,1,1,1"
	print "  python astrosib-cmd.py COM9 SHUTTERCLOSE?1,1,1,1,1"
	exit()
elif nbArgs!=3:
	print "mauvais nombre d arguments"
	exit()

# le port serie
print "ouvre le port serie, ",
com=sys.argv[1]
if com[0:3]=='COM':
	# on tourne sous windows
	comName=int(com[3:])-1
	print "  Port COM"+str(comName+1)
else:
	#on tourne pas sous windows
	comName=com
	print "  Port Dev: "+comName

ser = serial.Serial(comName,9600,timeout=1)

# la commande
command=sys.argv[2]
chaine=command+"\r"
print "chaineEnvoye="+chaine
ser.write(chaine)
print "ferme le port serie"
ser.flush()
ser.close()
