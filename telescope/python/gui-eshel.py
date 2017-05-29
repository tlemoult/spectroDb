#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# this program is a small GUI for control of the eShel calibration unit
# need to install the "pyserial" and python V2.7
# see:  http://pyserial.sourceforge.net/shortintro.html

# Author:  Thierry Lemoult
# date: November 28th, 2012

import Tkinter
import serial,time,sys

class simpleapp_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def handler(self):
		print("handler bye")		
		self.quit()

	def initialize(self):
		# change your com number here:   COM1=> comNumber=0,  COM2=> comNumber=1
		# le port serie
		print "ouvre le port serie, ",
		com=sys.argv[1]
		if com[0:3]=='COM':
			# on tourne sous windows
			self.comNumber=int(com[3:])-1
			print "  Port COM"+str(self.comNumber+1)
		else:
			#on tourne pas sous windows
			self.comNumber=com
			print "  Port Dev: "+self.comNumber
		self.miror=0b10000000
		self.led=0b01000000
		self.thAr=0b00100000
		self.tungsten=0b00010000
		self.start=13
		self.adress=1
		self.command=ord('B')
		self.protocol("WM_DELETE_WINDOW", self.handler)
		self.grid()

		buttonAon = Tkinter.Button(self,text=u"Lamp Off",command=self.OnButtonClickA)
		buttonAon.grid(column=0,row=0,columnspan=1,sticky='EW')
		buttonBon = Tkinter.Button(self,text=u"Led & tungsten",command=self.OnButtonClickB)
		buttonBon.grid(column=1,row=0,columnspan=1,sticky='EW')
		buttonCon = Tkinter.Button(self,text=u"tungsten",command=self.OnButtonClickC)
		buttonCon.grid(column=2,row=0,columnspan=1,sticky='EW')
		buttonDon = Tkinter.Button(self,text=u"Thorium Argon",command=self.OnButtonClickD)
		buttonDon.grid(column=3,row=0,columnspan=1,sticky='EW')

		self.grid_columnconfigure(0,weight=1)
		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())	   

	def SendOrder(self,param):
		check=256-((self.adress+self.start+self.command+param) % 256)
		cmd=[self.start,self.adress,self.command,param,check]
		print "send data to calibration modulemodule"
		print cmd
		cmds=chr(cmd[0])+chr(cmd[1])+chr(cmd[2])+chr(cmd[3])+chr(cmd[4])
		self.ser = serial.Serial(self.comNumber,2400,timeout=1)
		self.ser.write(cmds)
		self.ser.flush()
		self.ser.close()

	def OnButtonClickA(self):
		print "Lamp off"
		self.SendOrder(0)
	def OnButtonClickB(self):
		print "led & tungsten"
		self.SendOrder(self.led+self.miror+self.tungsten)
	def OnButtonClickC(self):
		print "tungsten"
		self.SendOrder(self.miror+self.tungsten)
	def OnButtonClickD(self):
		print "Thorium Argon"
		self.SendOrder(self.miror+self.thAr)

		
if __name__ == "__main__":

	if ( len(sys.argv)==1):
		print "Graphic user interface for eShell Calibration Module"
		print "Syntaxe:"
		print "python Pgui-eshel COM2"
		print "when serial port is COM2"
		exit()

	app = simpleapp_tk(None)
	app.title('eShel calibration unit control\nAuthor: Thierry Lemoult v1.01')
	
	app.mainloop()
	print("main bye")
	app.destroy()
	del app

