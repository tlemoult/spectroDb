import sys
import urllib

dns={'elec':'192.168.0.13', 'camera':'192.168.0.15' , 'info':'192.168.0.10'}
print("len(arvg)",len(sys.argv))
if ( len(sys.argv)!=3):
    print("exemple")
    print("python IPX800set.py elec 4=1")
    print("pour activer le relais 4 de l IPX800")
    print(" IPX connus: ")
    for k in dns.keys():
        print(str(k)+"--->"+dns[k])
    exit()

adress=sys.argv[1]

if adress in dns.keys():
    IPadress=dns[adress]
else:
    IPadress=adress

argno=sys.argv[2]
urlname="http://"+IPadress+"/preset.htm?set"+argno
print(urlname)
response = urllib.urlopen(urlname)
data=response.read()
	
