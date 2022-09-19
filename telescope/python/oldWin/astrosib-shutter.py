#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import serial
import sys
import urllib

print "Controle l ouverture et la fermeture des petales du telescope astrosib"

nbArgs=len(sys.argv)
if nbArgs==1:
	print "Syntaxe:"
	print "  python astrosib-shutter.py COM9 open"
	print "  python astrosib-shutter.py COM9 close"
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
if command=='open':
	print "open shutter"
	chaine="SHUTTEROPEN?1,1,1,1,1\r"
elif command=='close':
	print "close shutter"
	chaine="SHUTTERCLOSE?1,1,1,1,1\r"
else:
	chaine=""

print "chaineEnvoye="+chaine
ser.write(chaine)
print "ferme le port serie"
ser.flush()
ser.close()
