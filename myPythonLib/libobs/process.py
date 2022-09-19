
import libobs.IPX800 as IPX800
import libobs.powerControlSerial as powerControl
import libobs.astrosib as astrosib
import libobs.eShell as eShell
import time

def startup_observatory():
    relay_spectro = 2
    print("Power on the eShell spectro cupBoard")
    IPX800.set("IPX800elec",relay_spectro,True)
    time.sleep(0.5)
    print("power off eShell calibration lamp")
    eShell.set("off")

    relay_infor = 3
    print("Power up the info cubBoard")
    IPX800.set("IPX800elec",relay_infor,True)

    relay_camera = 1
    print("Power up video camera")
    IPX800.set("IPX800video",relay_camera,True)

    relay_power_box = 7
    print("Power up Power Control box")
    IPX800.set("IPX800info",relay_power_box,True)

    relay_mount = 6
    print("Power up mount")
    IPX800.set("IPX800info",relay_mount,True)

    time.sleep(0.5)

    relay_guide_camera = 1
    print("Power up Guide Camera")
    powerControl.set(relay_guide_camera,True)

    relay_astrosib = 4
    print("Power up astrosib telescope")
    powerControl.set(relay_astrosib,True)
    time.sleep(0.5)
    astrosib.set_shutter('OPEN')
    astrosib.set_heater(True)
    astrosib.set_cooler(True)

def shutdown_observatory():

    print("power off eShell calibration lamp")
    eShell.set("off")

    relay_spectro = 2
    print("Power down eShell spectro cupBoard")
    IPX800.set("IPX800elec",relay_spectro,False)

    print("Shutdown Astrosib Telescope")
    astrosib.set_shutter('CLOSE')
    astrosib.set_heater(False)
    astrosib.set_cooler(False)
    relay_astrosib = 4
    powerControl.set(relay_astrosib,False)

    relay_camera = 1
    print("Shutdown video camera")
    IPX800.set("IPX800video",relay_camera,False)

    relay_guide_camera = 1
    print("Power up Guide Camera")
    powerControl.set(relay_guide_camera,True)

    relay_power_box = 7
    print("Power down Power Control box")
    IPX800.set("IPX800info",relay_power_box,False)

    relay_mount = 6
    print("Power down mount")
    IPX800.set("IPX800info",relay_mount,False)



def main():
    print("Demo for observatory start up")

    startup_observatory()

    i_tot = 10
    for i in range(i_tot):
        time.sleep(1)
        print(f"Wait {i}/{i_tot} seconds",end="\r")

    shutdown_observatory()

    exit()

if __name__ == "__main__":
    main()	