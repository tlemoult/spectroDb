import os,time
from libobs import serialPort as serial

comDevice = "astrosib"

def _send_serial_wait(cmd,attended_response=''):
    print(f"Open serial port {comDevice}")
    ser = serial.Serial(comDevice,timeout=1)
    print(f"  send {repr(cmd)}")
    ser.write(bytes(cmd,'utf-8'))
    print(f"  wait response = {repr(attended_response)}")

    response = ''
    while not attended_response in response:
        response += ser.read().decode('utf-8')

    print(f"found in {repr(response)}")
    while not response.endswith('\r'):
        response += ser.read().decode('utf-8')

    print(f"Total response = {repr(response)}")
    ser.flush()
    ser.close()
    return response


def set_shutter(state):
    if state == 'OPEN':
        cmd = "SHUTTEROPEN?1,1,1,1,1\r"
    elif state == 'CLOSE':
        cmd = "SHUTTERCLOSE?1,1,1,1,1\r"
    response = _send_serial_wait(cmd,attended_response="SHUTTERS")
    if "0,0,0,0,0" in response:
        return "CLOSE"
    elif "1,1,1,1,1" in response:
        return "OPEN"
    else:
        return response

def get_shutter():
    cmd = "SHUTTERSTATUS?\r"
    response = _send_serial_wait(cmd,attended_response='SHUTTERS?')
    return response

def set_heater(state):
    if state:
        cmd = "HEATAUTOON?2\r"
    else:
        cmd = "HEATOFF?\r"
    response = _send_serial_wait(cmd,attended_response='OK')    
    return "OK" in response

def set_cooler(state):
    if state:
        cmd = "COOLERAUTOON?2\r"
    else:
        cmd = "COOLEROFF?\r"
    response = _send_serial_wait(cmd,attended_response='OK')
    return "OK" in response

def get_heater():
    cmd = "HEATSTATUS?\r"
    response = _send_serial_wait(cmd,attended_response='HEATERSTATUS')
    return response

def get_cooler():
    cmd = "COOLERSTATUS?\r"
    response = _send_serial_wait(cmd,attended_response='COOLERPWM')
    return response

def get_focus():
    print("*** get_focus()")
    cmd = "FOCUSERGPOS?\r"
    response = _send_serial_wait(cmd,attended_response='FOCUSERPOS')
    if "FOCUSERPOS?" in response:
        focuser_position = int(response.split("?")[-1])
        print(f"focuser focus is {focuser_position} step")
        return focuser_position
    else:   
        return None

def set_focus_abs(pos_abs,blocking=True):
    print(f"*** set_focus to {pos_abs})")
    global target_focus_abs
    target_focus_abs = pos_abs
    cmd = "FOCUSERGO?"+str(pos_abs)+"\r"
    if blocking:
        print("Wait until end of focus mouvment")
        _send_serial_wait(cmd,attended_response="FOCUSERPOS")
    else:
        print("exit before end of mouvment")
        response = _send_serial_wait(cmd,attended_response="OK")

def wait_focus():
    print("*** Wait_focus")
    actual_pos = get_focus()
    while actual_pos != target_focus_abs:
        print(f"Wait focuser Actual_pos = {actual_pos} ,  target_pos = {target_focus_abs} , error = {abs(actual_pos-target_focus_abs)}")
        time.sleep(1)
        actual_pos = get_focus()

def main():
    print("main demo for Astrosib telescope")


#    get_shutter()
#    set_heater(True)
#    set_cooler(True)
#    get_heater()
#    get_cooler()
#    get_focus()
#    set_shutter("OPEN")
#    set_shutter("CLOSE")

    get_focus()
    exit()

    set_focus_abs(30811,blocking = False)
    wait_focus()

    set_focus_abs(30011)

    exit()

if __name__ == "__main__":
    main()	
