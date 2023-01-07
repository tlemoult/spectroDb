#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

# this program is a small GUI for control of astrosib telescope
# need to install the "pyserial" and python V2.7
# see:  http://pyserial.sourceforge.net/shortintro.html

# Author:  Thierry Lemoult
# date: January 7 th, 2022

import tkinter
import time,sys,os
from libobs import astrosib as astrosib

focusPosition = None
focusStepSize = 5

class simpleapp_tk(tkinter.Tk):
	def __init__(self,parent):
		tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()

	def handler(self):
		print("handler bye")		
		self.quit()

	def initialize(self):
		global focusPosition,focusStepSize

		self.protocol("WM_DELETE_WINDOW", self.handler)
		self.grid()

		################################
		row = 0
		buttonAon = tkinter.Button(self,text="open shutter",command=self.OnButtonClickOpenShutter)
		buttonAon.grid(column=0,row=row,columnspan=1,sticky='EW')

		buttonBon = tkinter.Button(self,text="close shutter",command=self.OnButtonClickCloseShutter)
		buttonBon.grid(column=1,row=row,columnspan=1,sticky='EW')

		buttonHeaterCoolerOn = tkinter.Button(self,text="Set heater and cooler",command=self.OnButtonClickHeaterCoolerOn)
		buttonHeaterCoolerOn.grid(column=2,row=row,columnspan=1,sticky='EW')

		###########################
		row = row + 1
		labelHeaterStatus = tkinter.Label(self, text="heater status",anchor="e",fg="black")
		labelHeaterStatus.grid(column=0,row=row)

		self.HeaterStatusValue = tkinter.StringVar()
		labelHeaterStatusValue = tkinter.Label(self,textvariable=self.HeaterStatusValue,anchor="w",relief="sunken",borderwidth=3)
		labelHeaterStatusValue.grid(column=1,row=row,columnspan=1,sticky='EW')
		self.HeaterStatusValue.set(astrosib.get_heater())


		labelCoolerStatus = tkinter.Label(self, text="Cooler status",anchor="e",fg="black")
		labelCoolerStatus.grid(column=2,row=row)

		self.CoolerStatusValue = tkinter.StringVar()
		labelCoolerStatusValue = tkinter.Label(self,textvariable=self.CoolerStatusValue,anchor="w",relief="sunken",borderwidth=3)
		labelCoolerStatusValue.grid(column=3,row=row,columnspan=1,sticky='EW')
		self.CoolerStatusValue.set(astrosib.get_cooler())

		################################
		row = row + 1
		NameT1 = tkinter.Label(self, text="Focus position",anchor="e",fg="black")
		NameT1.grid(column=0,row=row)

		self.labelVarPosFocus = tkinter.StringVar()
		labelPosFocus = tkinter.Label(self,textvariable=self.labelVarPosFocus,anchor="w",relief="sunken",borderwidth=3)
		labelPosFocus.grid(column=1,row=row,columnspan=1,sticky='EW')
		focusPosition = astrosib.get_focus()
		self.labelVarPosFocus.set(str(focusPosition)) 

		
		##########################
		row = row + 1
		labelAbsFoc = tkinter.Label(self, text="abs position")
		labelAbsFoc.grid(column=0,row=row)

		#Create an Entry widget to accept User Input
		self.varFocAbs = tkinter.StringVar()
		entry= tkinter.Entry(self, textvariable = self.varFocAbs , width= 10)
		entry.grid(column=1,row=row,columnspan=1,sticky='EW')

		buttonSetAbs = tkinter.Button(self,text="set abs",command=self.OnButtonSetAbs)
		buttonSetAbs.grid(column=2,row=row,columnspan=1,sticky='EW')

		##########################
		row = row + 1
		colonStepStart = 1

		NameT1 = tkinter.Label(self, text="step size",anchor="e",fg="black")
		NameT1.grid(column=0,row=row)

		buttonSizeA = tkinter.Button(self,text="5",command=self.OnButtonClickstepSize5)
		buttonSizeA.grid(column=colonStepStart,row=row,columnspan=1,sticky='EW')
		colonStepStart = colonStepStart + 1

		buttonSizeB = tkinter.Button(self,text="10",command=self.OnButtonClickstepSize10)
		buttonSizeB.grid(column=colonStepStart,row=row,columnspan=1,sticky='EW')
		colonStepStart = colonStepStart + 1

		buttonSizeC = tkinter.Button(self,text="50",command=self.OnButtonClickstepSize50)
		buttonSizeC.grid(column=colonStepStart,row=row,columnspan=1,sticky='EW')
		colonStepStart = colonStepStart + 1

		#########################
		row = row + 1
		
		buttonDon = tkinter.Button(self,text="focus -",command=self.OnButtonClickFocusStepMinus)
		buttonDon.grid(column=0,row=row,columnspan=1,sticky='EW')

		buttonCon = tkinter.Button(self,text="focus +",command=self.OnButtonClickFocusStepPlus)
		buttonCon.grid(column=1,row=row,columnspan=1,sticky='EW')

		NameT2 = tkinter.Label(self, text="step size",anchor="e",fg="black")
		NameT2.grid(column=2,row=row)

		self.labelVarFocusStep = tkinter.StringVar()
		labelFocusStep = tkinter.Label(self,textvariable=self.labelVarFocusStep,anchor="w",relief="sunken",borderwidth=3)
		labelFocusStep.grid(column=3,row=row,columnspan=1,sticky='EW')
		self.labelVarFocusStep.set(str(focusStepSize))

		self.grid_columnconfigure(0,weight=1)
		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())	   


	def OnButtonClickOpenShutter(self):
		astrosib.set_shutter("OPEN")

	def OnButtonClickCloseShutter(self):
		astrosib.set_shutter("CLOSE")

	def OnButtonClickHeaterCoolerOn(self):
		astrosib.set_cooler(True)
		astrosib.set_heater(True)
		self.HeaterStatusValue.set(astrosib.get_heater())
		self.CoolerStatusValue.set(astrosib.get_cooler())

	def OnButtonClickFocusStepPlus(self):
		global focusPosition,focusStepSize
		focusPosition = focusPosition+focusStepSize
		print(f"focus step plus target = {focusPosition}")
		astrosib.set_focus_abs(focusPosition)
		self.labelVarPosFocus.set(str(focusPosition)) 


	def OnButtonClickFocusStepMinus(self):
		global focusPosition,focusStepSize
		focusPosition = focusPosition-focusStepSize
		print(f"focus step minus target = {focusPosition}")
		astrosib.set_focus_abs(focusPosition)
		self.labelVarPosFocus.set(str(focusPosition)) 

	def OnButtonClickstepSize5(self):
		global focusStepSize
		print(f"define step size to 5")
		focusStepSize = 5
		self.labelVarFocusStep.set(str(focusStepSize))

	def OnButtonClickstepSize10(self):
		global focusStepSize
		print(f"define step size to 10")
		focusStepSize = 10
		self.labelVarFocusStep.set(str(focusStepSize))

	def OnButtonClickstepSize50(self):
		global focusStepSize
		print(f"define step size to 50")
		focusStepSize = 50
		self.labelVarFocusStep.set(str(focusStepSize))

	def OnButtonSetAbs(self):
		global focusPosition
		inputFocusPosition = self.varFocAbs.get()
		focusPosition = int(inputFocusPosition)
		print(f"set focus position to {focusPosition}")
		astrosib.set_focus_abs(focusPosition)
		self.labelVarPosFocus.set(str(focusPosition))

if __name__ == "__main__":

	app = simpleapp_tk(None)
	app.title('astrosib gui')
	
	app.mainloop()
	print("main bye")
	app.destroy()
	del app

