import requests
import json,os,sys

if len(sys.argv) != 4:
	print(f"usage python3 clientFinder.py ipServer portServer outputFile")
	exit()

ipServer=sys.argv[1]
portServer=sys.argv[2]
outputfile=sys.argv[3]

url = "http://"+ipServer+":"+str(portServer)+"/api/finder"

#outputfile  = "./finderOutput.txt"

try:
    os.remove(outputfile)
except:
    print(f"no file {outputfile} to remove")

print(f"Request Finder server URL = {url}\n")
response = requests.get(url)
print(f"response status code = {response.status_code}")
print(json.dumps(response.json(), indent=4))

if response.status_code == 200:
    print(f"API success, Write result file {outputfile}")
    f1 = open(outputfile,"w")
    f1.write("#output file from finder, first RA, then DEC in Radian\n")
    f1.write(f"{response.json()['coord']['RA']}\n")
    f1.write(f"{response.json()['coord']['DEC']}\n")
    f1.close()
else:
    print("error status = {response.status_code}")

