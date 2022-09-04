#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# this program is a small GUI for control of the eShel calibration unit
# need to install the "pyserial" and python V2.7
# see:  http://pyserial.sourceforge.net/shortintro.html

# Author:  Thierry Lemoult
# date: November 28th, 2012

import tkinter
import serial,time,sys,os

class simpleapp_tk(tkinter.Tk):
	def __init__(self,parent):
		tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def handler(self):
		print("handler bye")		
		self.quit()

	def initialize(self):
		print("do not forget , spectroDb/telescope/linuxScript/goSocat.sh")
		self.comDevice = os.path.expanduser("~/.local/dev/ttyEshel")
#		self.comDevice = os.path.expanduser("~/.local/dev/ttyDome")
		print(f"Eshel com device = {self.comDevice}")

		self.miror=0b10000000
		self.led=0b01000000
		self.thAr=0b00100000
		self.tungsten=0b00010000
		self.start=13
		self.adress=1
		self.command=ord('B')
		self.protocol("WM_DELETE_WINDOW", self.handler)
		self.grid()

		buttonAon = tkinter.Button(self,text="Lamp Off",command=self.OnButtonClickA)
		buttonAon.grid(column=0,row=0,columnspan=1,sticky='EW')
		buttonBon = tkinter.Button(self,text="Led & tungsten",command=self.OnButtonClickB)
		buttonBon.grid(column=1,row=0,columnspan=1,sticky='EW')
		buttonCon = tkinter.Button(self,text="tungsten",command=self.OnButtonClickC)
		buttonCon.grid(column=2,row=0,columnspan=1,sticky='EW')
		buttonDon = tkinter.Button(self,text="Thorium Argon",command=self.OnButtonClickD)
		buttonDon.grid(column=3,row=0,columnspan=1,sticky='EW')

		self.grid_columnconfigure(0,weight=1)
		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())	   

	def SendOrder(self,param):
		check=256-((self.adress+self.start+self.command+param) % 256)
		cmd=[self.start,self.adress,self.command,param,check]
		print("send data to eShell calibration module")
		print(f"decimal cmd = {cmd}")
		bytesCmd = bytes(cmd)
		print(f"byteCmd = {bytesCmd}")
		self.ser = serial.Serial(self.comDevice,2400,timeout=1)
		self.ser.write(bytesCmd)
		self.ser.flush()
		self.ser.close()

	def OnButtonClickA(self):
		print("Lamp off")
		self.SendOrder(0)
	def OnButtonClickB(self):
		print("led & tungsten")
		self.SendOrder(self.led+self.miror+self.tungsten)
	def OnButtonClickC(self):
		print("tungsten")
		self.SendOrder(self.miror+self.tungsten)
	def OnButtonClickD(self):
		print("Thorium Argon")
		self.SendOrder(self.miror+self.thAr)

		
if __name__ == "__main__":

	app = simpleapp_tk(None)
	app.title('eShel calibration unit control\nAuthor: Thierry Lemoult v1.01')
	
	app.mainloop()
	print("main bye")
	app.destroy()
	del app

