import requests

# adress string IP or name..
# state True or False
# relay 1,2,3,4,5,6,7,8  
# IPX800.set('ipx800video',relay=1,state=True)
def set(adress,relay,state):

    if state:
        state_str = '1'
    else:
        state_str = '0'

    url_name="http://"+adress+"/preset.htm?set"+str(relay)+"="+state_str
    print(f"IPX800.set({url_name})")
    r = requests.get(url_name)

    #print(f"response = {r.text}")

def main():
    print("main demo for IPX800 control")

    set("IPX800video",1,False)

if __name__ == "__main__":
    main()	