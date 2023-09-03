
import libobs.IPX800 as IPX800
import libobs.powerControl as powerControl
import libobs.astrosib as astrosib
import libobs.eShell as eShell
import time

def startup_observatory(spectro='LISA'):

    print(f"**** startup_observatory with spectro = {spectro}")

    if spectro == 'eShel':
        # this need early wake up.., need time to start
        relay_spectro = 2
        print("Power on the eShell spectro cupBoard")
        IPX800.set("IPX800elec",relay_spectro,True)

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
    timeWait = 3
    print(f"wait {timeWait} seconds , startup of PowerControl etc.....")
    time.sleep(timeWait)

    relay_astrosib = 4
    powerControl.set(relay_astrosib,True)
    timeWait = 3
    print(f"wait {timeWait} Power up astrosib telescope")
    time.sleep(timeWait)

    astrosib.set_shutter('OPEN')
    astrosib.set_heater(True)
    astrosib.set_cooler(True)

    if spectro == 'LISA':

        relay_camera_telescope = 3
        print("Power up LISA Camera telescope 12V")
        IPX800.set("IPX800info",relay_camera_telescope,True)

        relay_spectrum_camera = 7
        print("Power up the LISA spectra camera")
        powerControl.set(relay_spectrum_camera,True)

        print("shutdown LISA calibration lamp")
        relay_calib_neon = 5
        powerControl.set(relay_calib_neon,False)
        relay_flat_lamp = 6
        powerControl.set(relay_flat_lamp,False)

    if spectro == 'eShel':
        relay_guide_camera = 1
        print("Power up Guide Camera")
        powerControl.set(relay_guide_camera,True)

        print("power off eShell calibration lamp")
        eShell.set("off")

    timeWait = 3
    print(f"wait {timeWait} seconds , after startup_observatory")
    print("allow camera startup etc..")
    time.sleep(timeWait)


def shutdown_observatory(spectro='LISA'):

    if spectro == 'eShel':
        print("power off eShell calibration lamp")
        eShell.set("off")

        relay_spectro = 2
        print("Power down eShell spectro cupBoard")
        IPX800.set("IPX800elec",relay_spectro,False)

    elif spectro == 'LISA':

        relay_camera_telescope = 3
        print("shutdown LISA Camera telescope 12V")
        IPX800.set("IPX800info",relay_camera_telescope,False)

        print("shutdown the LISA spectra camera")
        relay_spectrum_camera = 7
        powerControl.set(relay_spectrum_camera,False)
        print("shutdown LISA calibration lamp")
        relay_calib_neon = 5
        powerControl.set(relay_calib_neon,False)
        relay_flat_lamp = 6
        powerControl.set(relay_flat_lamp,False)

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
    print("Power down Guide Camera")
    powerControl.set(relay_guide_camera,False)

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