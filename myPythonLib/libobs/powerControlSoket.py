import socket

# this module drive an home made with arduino power box with relay

# serial_port = 1

def set(adress,serial_port,relay,state):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 4000+ serial_port
    print(f"Connect to socket adress = {adress}:{port}")

    s.connect( (adress, port))

    relay_no_byte = bytes(str(relay),'utf-8')

    if state:
        relay_state_byte = b'1'
    else:
        relay_state_byte = b'0'

    print(f"relay number {relay} set to {state}")

    order_bytes = b'R'+relay_no_byte+relay_state_byte+b'\n'
    print(f"order_byte = {order_bytes}")

    s.send(order_bytes)
    print("Close Socket")
    s.close()    


def main():
    print("main demo for power control")

    set("moxadome",1,1,True)
    #set("moxa1",2,3,True)

if __name__ == "__main__":
    main()