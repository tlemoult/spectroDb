import socket,logging,sys,json,time

class GuiderPHP2():

    def __init__(self,host,port):
        self.logger = logging.getLogger('clientPHD2')        
        self.logger.info('creating an instance of GuiderPHP2')
        self.host=str(host)
        self.port=port
        self.id=1

    def connect(self):
        self.logger.info("<<<<<<< connect to server PHD2 server=%s  port=%d"%(self.host,self.port))

        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.setblocking(0)
        self.sock.settimeout(1.0)

        try:
            # Connect to server and send data
            self.sock.connect((self.host, self.port))
        except:
            self.logger.error("connection failed server PHD2 server=%s  port=%d"%(self.host,self.port))
            print sys.exc_info()[0]
            return "error"

        received = self.sock.recv(1024)
        return received

    def sendJson(self,jsonTxt):
        try:
            self.sock.sendall(jsonTxt)
        except:
            self.logger.error("sendJSON failed")
            return ""

        # Receive data from the server
        received = self.sock.recv(1024)
        self.logger.info("Receive %s"%(received))
        return received

    def closeServer(self):
        self.logger.info("<<<<<<< connection close with server PHD2")
        self.sock.close()

    def setConsigne(self,posX,posY):
        jsonTxt='{"jsonrpc":"2.0", "method": "set_lock_position", "params": {"x":%.1f , "y":%.1f }, "id":%d } \r\n'%(posX,posY,self.id)
        self.id+=1
        self.logger.info("send msg %s"%jsonTxt)
        return self.sendJson(jsonTxt)

    def setExposure(self,exposure):
        exposureMilli=int(exposure*1000)
        jsonTxt='{"jsonrpc":"2.0", "method": "set_exposure", "params": [%d], "id": %d} \r\n'%(exposureMilli,self.id)
        self.id+=1
        self.logger.info("send msg %s"%jsonTxt)
        return self.sendJson(jsonTxt)

    def loop(self):
        jsonTxt='{"jsonrpc":"2.0", "method": "loop", "params": [], "id":%d } \r\n'%(self.id)
        self.id+=1
        self.logger.info("send msg %s"%jsonTxt)
        return self.sendJson(jsonTxt)

    def stop(self):
        jsonTxt='{"jsonrpc":"2.0", "method": "stop_capture", "params": [], "id":%d } \r\n'%(self.id)
        self.id+=1
        self.logger.info("send msg %s"%jsonTxt)
        return self.sendJson(jsonTxt)

    def guide(self):
        jsonTxt='{"jsonrpc":"2.0", "method": "guide", "params": [{"pixels": 1.5, "time": 8, "timeout": 40}, false], "id":%d } \r\n'%(self.id)
        self.id+=1
        self.logger.info("send msg %s"%jsonTxt)
        return self.sendJson(jsonTxt)

    def receive(self):
        # Receive data from the server
        try:
            received = self.sock.recv(1024)
        except socket.timeout:
            self.logger.info("No response from server")
            return ""
        return received
        
#https://dzone.com/articles/understanding

jsonTxt=open('./configAcquire.json').read()
config=json.loads(jsonTxt)
print config

# setup log file
logging.basicConfig(filename=config['PHD2']['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

# instantiate Guider class, set server and port
server=config['PHD2']['server']
guiderPHD2=GuiderPHP2(server['host'],server['port'])

#connect
received=guiderPHD2.connect()
print "received",received

received=guiderPHD2.receive()
print "received",received

#set consigne
received=guiderPHD2.setConsigne(76.1,145.2)
print "received",received

received=guiderPHD2.receive()
print "received",received


#set exposure
received=guiderPHD2.setExposure(1.0)
print "received",received

received=guiderPHD2.receive()
print "received",received

#start loop
received=guiderPHD2.loop()
print "received",received


#start guide
received=guiderPHD2.guide()
print "received",received



received=guiderPHD2.receive()
print "received",received




# attente
st=5
print "wait %d sec"%st
time.sleep(st)

received=guiderPHD2.stop()
print "received",received

received=guiderPHD2.receive()
print "received",received

#close connection
guiderPHD2.closeServer()
