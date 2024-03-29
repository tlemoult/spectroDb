#json writer


def write(path,objName,isRef,ra,dec,project,confInstru,site,observer):
	print("Create observation.json file")

	f=open(path+'/observation.json','w')
	f.write("""{
 "Comment": "acquisition JSON file generated by python after parsing of filename", 
  "jsonType": "acquisitionFile", 
 "formatVersion": "0.0.1",  

 "target": {
     "objname": ["""+'"'+str(objName)+'"],\n')
	f.write('     "isRef":')
	if isRef: f.write('true,\n') 
	else: f.write('false,\n')
	f.write('    "coord": {\n')
	f.write('       "ra" :'+'"'+str(ra)+'",\n')
	f.write('       "dec" :'+'"'+str(dec)+'",\n')
	f.write('       "equinox": "J2000" \n')
	f.write('      }\n')
	f.write('  },\n')
	f.write('\n')
	
	f.write('"project": "'+str(project)+'",\n')
	
	f.write('"instrument":  { \n')
	f.write('   "telescop": "'+confInstru['telescop']+'",\n')
	f.write('   "configName": "'+confInstru['configName']+'",\n')
	f.write('   "spectro": "'+confInstru['spectro']+'",\n')
	f.write('   "detname": "'+confInstru['detname']+'",\n')
	f.write('   "guideDetname": "'+confInstru['guideDetname']+'",\n')	
	f.write('   "resol":   '+str(int(confInstru['resol']))+'\n')
	f.write('},\n')

	f.write('"site": {\n')
	f.write('   "name":"'+site['name']+'",\n')
	f.write('   "country":"'+site['country']+'",\n')
	f.write('   "lat":"'+site['lat']+'",\n')
	f.write('   "lon":"'+site['lon']+'",\n')
	f.write('   "alt":"'+site['alt']+'",\n')
	f.write('   "UAIcode":"'+site['UAIcode']+'"\n')
	f.write('},\n')

	f.write('"observer": {\n')
	f.write('     "firstName":"'+observer['firstName']+'",\n')
	f.write('     "lastName":"'+observer['lastName']+'",\n')
	f.write('     "email":"'+observer['email']+'",\n')
	f.write('     "alias":"'+observer['alias']+'"\n')
	f.write('}\n')
	f.write('\n')
	f.write('\n')
	f.write('\n')

	f.write("}\n")
	f.close()

