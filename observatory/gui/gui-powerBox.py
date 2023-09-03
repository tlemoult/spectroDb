#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import tkinter
from libobs import serialPort as serial
import time,os
# see:  http://pyserial.sourceforge.net/shortintro.html

class simpleapp_tk(tkinter.Tk):
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent
        
        self.initialize()

    def handler(self):
        print("gui-powerBox handler bye")
        self.closeSerial()
        self.quit()

    def openSerial(self):
        self.ser = serial.Serial(self.comDevice,timeout=1)

    def closeSerial(self):
        self.ser.close()

    def writeSerial(self,data_string):
        self.openSerial()
        self.ser.write(bytes(data_string,'utf-8'))
        self.ser.flush()
        self.closeSerial()

    def initialize(self):
        self.comDevice = "powerControl"
        print(f"com device = {self.comDevice}")

        self.protocol("WM_DELETE_WINDOW", self.handler)
        
        self.grid()

        NameA = tkinter.Label(self, text="(1)\nCamera\nGuide",anchor="w",fg="white",bg="black",width=8)
        NameA.grid(column=0,row=0)
        NameB = tkinter.Label(self, text="(2)\nFree",anchor="w",fg="black",bg="white",width=8)
        NameB.grid(column=1,row=0)
        NameC = tkinter.Label(self, text="(3)\nFree",anchor="w",fg="white",bg="black")
        NameC.grid(column=2,row=0)
        NameD = tkinter.Label(self, text="(4)\nAstrosib\nTelescope",anchor="w",fg="black",bg="white",width=8)
        NameD.grid(column=3,row=0)
        NameE = tkinter.Label(self, text="(5)\nNeon",anchor="w",fg="white",bg="black")
        NameE.grid(column=4,row=0)
        NameF = tkinter.Label(self, text="(6)\nFlat",anchor="w",fg="black",bg="white")
        NameF.grid(column=5,row=0)
        NameG = tkinter.Label(self, text="(7)\nCamera\nSpectro",anchor="w",fg="white",bg="black")
        NameG.grid(column=6,row=0)
        NameH = tkinter.Label(self, text="(8)\nFree",anchor="w",fg="black",bg="white")
        NameH.grid(column=7,row=0)
        NameT = tkinter.Label(self, text="Temperature\nSensor",anchor="w",fg="white",bg="black")
        NameT.grid(column=8,row=0)
        NameT1 = tkinter.Label(self, text="Exterior",anchor="e",fg="black",bg="grey")
        NameT1.grid(column=8,row=1)
        NameT2 = tkinter.Label(self, text="Interior",anchor="e",fg="black",bg="grey")
        NameT2.grid(column=8,row=2)
        NameVO = tkinter.Label(self, text="Voltage",anchor="e",fg="black",bg="grey")
        NameVO.grid(column=8,row=3)
        

       
        buttonAon = tkinter.Button(self,text="On",command=self.OnButtonClickA)
        buttonAon.grid(column=0,row=1,columnspan=1,sticky='EW')
        buttonBon = tkinter.Button(self,text="On",command=self.OnButtonClickB)
        buttonBon.grid(column=1,row=1,columnspan=1,sticky='EW')
        buttonCon = tkinter.Button(self,text="On",command=self.OnButtonClickC)
        buttonCon.grid(column=2,row=1,columnspan=1,sticky='EW')
        buttonDon = tkinter.Button(self,text="On",command=self.OnButtonClickD)
        buttonDon.grid(column=3,row=1,columnspan=1,sticky='EW')
        buttonEon = tkinter.Button(self,text="On",command=self.OnButtonClickE)
        buttonEon.grid(column=4,row=1,columnspan=1,sticky='EW')
        buttonFon = tkinter.Button(self,text="On",command=self.OnButtonClickF)
        buttonFon.grid(column=5,row=1,columnspan=1,sticky='EW')
        buttonGon = tkinter.Button(self,text="On",command=self.OnButtonClickG)
        buttonGon.grid(column=6,row=1,columnspan=1,sticky='EW')
        buttonHon = tkinter.Button(self,text="On",command=self.OnButtonClickH)
        buttonHon.grid(column=7,row=1,columnspan=1,sticky='EW')


        buttonAoff = tkinter.Button(self,text="Off",command=self.OffButtonClickA)
        buttonAoff.grid(column=0,row=3,columnspan=1,sticky='EW')
        buttonBoff = tkinter.Button(self,text="Off",command=self.OffButtonClickB)
        buttonBoff.grid(column=1,row=3,columnspan=1,sticky='EW')
        buttonCoff = tkinter.Button(self,text="Off",command=self.OffButtonClickC)
        buttonCoff.grid(column=2,row=3,columnspan=1,sticky='EW')
        buttonDoff = tkinter.Button(self,text="Off",command=self.OffButtonClickD)
        buttonDoff.grid(column=3,row=3,columnspan=1,sticky='EW')
        buttonEoff = tkinter.Button(self,text="Off",command=self.OffButtonClickE)
        buttonEoff.grid(column=4,row=3,columnspan=1,sticky='EW')
        buttonFoff = tkinter.Button(self,text="Off",command=self.OffButtonClickF)
        buttonFoff.grid(column=5,row=3,columnspan=1,sticky='EW')
        buttonGoff = tkinter.Button(self,text="Off",command=self.OffButtonClickG)
        buttonGoff.grid(column=6,row=3,columnspan=1,sticky='EW')
        buttonHoff = tkinter.Button(self,text="Off",command=self.OffButtonClickH)
        buttonHoff.grid(column=7,row=3,columnspan=1,sticky='EW')

        buttonUpdate = tkinter.Button(self,text="Refresh",command=self.UpdateInfo)
        buttonUpdate.grid(column=9,row=0,columnspan=1,sticky='EW')


        self.labelVariableA = tkinter.StringVar()
        self.labelA = tkinter.Label(self,textvariable=self.labelVariableA,anchor="w",relief="sunken",borderwidth=3)
        self.labelA.grid(column=0,row=2,columnspan=1,sticky='EW')
        self.labelVariableA.set("     ")


        self.labelVariableB = tkinter.StringVar()
        self.labelB = tkinter.Label(self,textvariable=self.labelVariableB,anchor="w",relief="sunken",borderwidth=3)
        self.labelB.grid(column=1,row=2,columnspan=1,sticky='EW')
        self.labelVariableB.set("    ")

        
        self.labelVariableC = tkinter.StringVar()
        self.labelC = tkinter.Label(self,textvariable=self.labelVariableC,anchor="w",relief="sunken",borderwidth=3)
        self.labelC.grid(column=2,row=2,columnspan=1,sticky='EW')
        self.labelVariableC.set("    ")
 

        self.labelVariableD = tkinter.StringVar()
        self.labelD = tkinter.Label(self,textvariable=self.labelVariableD,anchor="w",relief="sunken",borderwidth=3)
        self.labelD.grid(column=3,row=2,columnspan=1,sticky='EW')
        self.labelVariableD.set("     ")


        self.labelVariableE = tkinter.StringVar()
        self.labelE = tkinter.Label(self,textvariable=self.labelVariableE,anchor="w",relief="sunken",borderwidth=3)
        self.labelE.grid(column=4,row=2,columnspan=1,sticky='EW')
        self.labelVariableE.set("     ")
 

        self.labelVariableF = tkinter.StringVar()
        self.labelF = tkinter.Label(self,textvariable=self.labelVariableF,anchor="w",relief="sunken",borderwidth=3)
        self.labelF.grid(column=5,row=2,columnspan=1,sticky='EW')
        self.labelVariableF.set("     ")

        self.labelVariableG = tkinter.StringVar()
        self.labelG = tkinter.Label(self,textvariable=self.labelVariableG,anchor="w",relief="sunken",borderwidth=3)
        self.labelG.grid(column=6,row=2,columnspan=1,sticky='EW')
        self.labelVariableG.set("     ")

        self.labelVariableH = tkinter.StringVar()
        self.labelH = tkinter.Label(self,textvariable=self.labelVariableH,anchor="w",relief="sunken",borderwidth=3)
        self.labelH.grid(column=7,row=2,columnspan=1,sticky='EW')
        self.labelVariableH.set("     ")

        self.labelVariableT1 = tkinter.StringVar()
        labelT1 = tkinter.Label(self,textvariable=self.labelVariableT1,anchor="w",relief="sunken",borderwidth=3)
        labelT1.grid(column=9,row=1,columnspan=1,sticky='EW')
        self.labelVariableT1.set("00.0 C")
       
        self.labelVariableT2 = tkinter.StringVar()
        labelT2 = tkinter.Label(self,textvariable=self.labelVariableT2,anchor="w",relief="sunken",borderwidth=3)
        labelT2.grid(column=9,row=2,columnspan=1,sticky='EW')
        self.labelVariableT2.set("00.0 C")

        self.labelVariableVO = tkinter.StringVar()
        labelVO = tkinter.Label(self,textvariable=self.labelVariableVO,anchor="w",relief="sunken",borderwidth=3)
        labelVO.grid(column=9,row=3,columnspan=1,sticky='EW')
        self.labelVariableVO.set("00.0 V")


        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()

        time.sleep(1)
        self.UpdateInfo()
        #self.geometry(self.geometry())       


    def UpdateInfo(self):
        self.openSerial()
        self.ser.write(bytes("S\n",'utf-8'))
        self.ser.flush()
        relayState=self.ser.readline().decode('utf-8')
        

        if relayState[1]=='1':
            self.labelVariableA.set("  On")
            self.labelA.config(fg="white",bg="green")
        else:
            self.labelVariableA.set("  Off")
            self.labelA.config(fg="black",bg="grey")

        if relayState[2]=='1':
            self.labelVariableB.set("  On")
            self.labelB.config(fg="white",bg="green")
        else:
            self.labelVariableB.set("  Off")
            self.labelB.config(fg="black",bg="grey")

        if relayState[3]=='1':
            self.labelVariableC.set("  On")
            self.labelC.config(fg="white",bg="green")
        else:
            self.labelVariableC.set("  Off")
            self.labelC.config(fg="black",bg="grey")

        if relayState[4]=='1':
            self.labelVariableD.set("  On")
            self.labelD.config(fg="white",bg="green")
        else:
            self.labelVariableD.set("  Off")
            self.labelD.config(fg="black",bg="grey")

        if relayState[5]=='1':
            self.labelVariableE.set("  On")
            self.labelE.config(fg="white",bg="green")
        else:
            self.labelVariableE.set("  Off")
            self.labelE.config(fg="black",bg="grey")

        if relayState[6]=='1':
            self.labelVariableF.set("  On")
            self.labelF.config(fg="white",bg="green")
        else:
            self.labelVariableF.set("  Off")
            self.labelF.config(fg="black",bg="grey")

        if relayState[7]=='1':
            self.labelVariableG.set("  On")
            self.labelG.config(fg="white",bg="green")
        else:
            self.labelVariableG.set("  Off")
            self.labelG.config(fg="black",bg="grey")

        if relayState[8]=='1':
            self.labelVariableH.set("  On")
            self.labelH.config(fg="white",bg="green")
        else:
            self.labelVariableH.set("  Off")
            self.labelH.config(fg="black",bg="grey")

        # get data from sensor
        self.labelVariableT2.set((self.ser.readline()[2:6]).decode('utf-8')+" C")
        self.labelVariableT1.set((self.ser.readline()[2:6]).decode('utf-8')+" C")
        self.labelVariableVO.set((self.ser.readline()[2:6]).decode('utf-8')+" V")
        self.closeSerial()

    def Refresh(self):
        self.labelVariableF.set("On")
        self.labelVariableE.set("On")

    def OnButtonClickA(self):
        self.writeSerial("R01\n")
        self.UpdateInfo()
    def OffButtonClickA(self):
        self.writeSerial("R00\n")
        self.UpdateInfo()
    def OnButtonClickB(self):
        self.writeSerial("R11\n")
        self.UpdateInfo()
    def OffButtonClickB(self):
        self.writeSerial("R10\n")
        self.UpdateInfo()
    def OnButtonClickC(self):
        self.writeSerial("R21\n")
        self.UpdateInfo()
    def OffButtonClickC(self):
        self.writeSerial("R20\n")
        self.ser.flush()
        self.UpdateInfo()
    def OnButtonClickD(self):
        self.writeSerial("R31\n")
        self.UpdateInfo()
    def OffButtonClickD(self):
        self.writeSerial("R30\n")
        self.UpdateInfo()
    def OnButtonClickE(self):
        self.writeSerial("R41\n")
        self.UpdateInfo()
    def OffButtonClickE(self):
        self.writeSerial("R40\n")
        self.UpdateInfo()
    def OnButtonClickF(self):
        self.writeSerial("R51\n")
        self.UpdateInfo()
    def OffButtonClickF(self):
        self.writeSerial("R50\n")
        self.UpdateInfo()
    def OnButtonClickG(self):
        self.writeSerial("R61\n")
        self.UpdateInfo()
    def OffButtonClickG(self):
        self.writeSerial("R60\n")
        self.UpdateInfo()
    def OnButtonClickH(self):
        self.writeSerial("R71\n")
        self.UpdateInfo()
    def OffButtonClickH(self):
        self.writeSerial("R70\n")
        self.UpdateInfo()
        
if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('Chelles observatory, Arduino Power box  v1.15 2022')
    
    app.mainloop()
    #print("main bye")
    app.destroy()
    del app

