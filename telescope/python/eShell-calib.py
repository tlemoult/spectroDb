#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import serial
import sys
import urllib

print "Passage d une commande au module calibration eShel"

nbArgs=len(sys.argv)
if nbArgs==1:
	print "Syntaxe:"
	print "  python eShell-calib.py COM7 off"
	print "  python eShell-calib.py COM7 calib"
	print "  python eShell-calib.py COM7 led"
	print "  python eShell-calib.py COM7 flat"
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

ser = serial.Serial(comName,2400,timeout=1)

# commande
miror=0b10000000
led=0b01000000
thAr=0b00100000
tungsten=0b00010000
cmdDict={'led':miror+led+tungsten,'off':0,'calib':miror+thAr,'flat':miror+tungsten}

start=13
adress=1
command=ord('B')

try:
    param=cmdDict[sys.argv[2]]
except:
    print "unknow command: ", sys.argv[2]
    print "try one of this",cmdDict.keys()
    ser.close()

check=256-((adress+start+command+param) % 256)
cmd=[start,adress,command,param,check]
print "send data to calibration module"
print cmd
cmds=chr(cmd[0])+chr(cmd[1])+chr(cmd[2])+chr(cmd[3])+chr(cmd[4])

ser.write(cmds)
ser.flush()


ser.close()

