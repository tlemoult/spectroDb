#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


import serial
import sys
import urllib

comNumber=2

if ( len(sys.argv)==1):
	print "Controle etat des relais de l'interface faite maison"
	print "Syntaxe:"
	print "python PowerBoxset.py 4=1"
	print "pour activer le relais 4"
	exit()
	
print "Power Box Serial Port COM"+str(comNumber)

relNo=sys.argv[1][0]
relState=sys.argv[1][2]

#pour l usb de l arduino, on utilise dstr=1
#ser = serial.Serial(2,9600,timeout=1,dsrdtr=1)

#vrais port serie, pas de dsr dtr
ser = serial.Serial(comNumber-1,9600,timeout=1)
chaine="R"+relNo+relState+"\n"
print "chaine="+chaine
ser.write(chaine)
ser.flush()
ser.close()

