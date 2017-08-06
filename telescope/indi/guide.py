import socket,logging,sys,json,time

from lib.GuiderPHP2 import GuiderPHP2 as GuiderPHP2

#exemple of asyncronus socket: https://dzone.com/articles/understanding
# see here PHD2 protocol:  https://github.com/OpenPHDGuiding/phd2/wiki/EventMonitoring

#load configuration file
jsonTxt=open('./configAcquire.json').read()
config=json.loads(jsonTxt)
print (config)
print ("--------------")

# setup log file
logging.basicConfig(filename=config['PHD2']['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

# instantiate Guider class, set server and port
server=config['PHD2']['server']
guiderPHD2=GuiderPHP2(server['host'],server['port'])

#connect
guiderPHD2.connect()

#set consigne
posX=float(config['PHD2']['posX'])
posY=float(config['PHD2']['posY'])
guiderPHD2.setConsigne(posX,posY)

#set exposure time
guiderPHD2.setExposure(1.0)

guiderPHD2.getResponse()
print("app state=%s"%guiderPHD2.appState)

#start loop
guiderPHD2.loop()

#start guide
guiderPHD2.guide()
guiderPHD2.getResponse()

# attente
st=15
print("wait %d sec"%st)
for i in range(st):
    time.sleep(1)
    guiderPHD2.getResponse()

#stop guiding
guiderPHD2.stop()
guiderPHD2.getResponse()

#close connection
guiderPHD2.closeServer()
