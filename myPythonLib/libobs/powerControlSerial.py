import serial,os

# this module drive an home made with arduino power box with relay
comDevice = os.path.expanduser("~/.local/dev/ttyPowerControl")

def set(relay,state):

    print(f"Open serial port {comDevice}")
    ser = serial.Serial(comDevice,9600,timeout=1)

    relay_no_byte = bytes(str(relay-1),'utf-8')

    if state:
        relay_state_byte = b'1'
    else:
        relay_state_byte = b'0'

    print(f"relay number {relay} set to {state}")

    order_bytes = b'R'+relay_no_byte+relay_state_byte+b'\n'
    print(f"order_byte = {order_bytes}")

    ser.write(order_bytes)
    print("Close Serial Port")
    ser.close()


def main():
    print("main demo for power control")

    set(1,False)
    set(2,True)

if __name__ == "__main__":
    main()