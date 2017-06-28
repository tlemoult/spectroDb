import socket,logging,sys,json

class GuiderPHP2():

    def __init__(self):
        self.logger = logging.getLogger('clientPHD2')        
        self.logger.info('creating an instance of GuiderPHP2')

    def connectServer(self,server,port):
        self.logger.info("<<<<<<< connect to server PHD2 server=%s  port=%d"%(server,port))

        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            self.sock.connect((str(server), port))
        except:
            self.logger.error("connection failed server PHD2 server=%s  port=%d"%(server,port))
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


json_text=open('./configAcquire.json').read()
config=json.loads(json_text)
print config

# setup log file
logging.basicConfig(filename=config['PHD2']['logFile'],level=logging.DEBUG,format='%(asctime)s %(message)s')

guiderPHD2=GuiderPHP2()
server=config['PHD2']['server']

received=guiderPHD2.connectServer(str(server['host']),server['port'])
print "received",received

#guiderPHD2.sendJson('{"test":3}')
guiderPHD2.closeServer()
