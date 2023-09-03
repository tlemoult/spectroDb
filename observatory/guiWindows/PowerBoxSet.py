#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


import serial
import sys
import urllib

if ( len(sys.argv)==1):
	print "Controle etat des relais de l'interface faite maison"
	print "Syntaxe:"
	print "python PowerBoxset.py COM2 4=1"
	print "pour activer le relais 4, avec powerbox sur le port serie COM2"
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

#on recupere la commande
relNo=sys.argv[2][0]
relState=sys.argv[2][2]

# execute la commande
ser = serial.Serial(comName,9600,timeout=1)
chaine="R"+relNo+relState+"\n"
print "chaine="+chaine
ser.write(chaine)
ser.flush()
ser.close()

