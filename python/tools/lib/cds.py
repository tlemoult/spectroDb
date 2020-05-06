from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

def getCoord(obj):
	r=Simbad.query_object(obj)
	
	d={}
	for key in ['RA','DEC']:
		try:
			d[key]=str(r[key]).split('\n')[3]
		except:
			d[key]=None;
			
	if d['RA']==None:	# on n a pas trouve les coords.. objet inconnus du CDS
		d={}

	return d


def getHD_and_BayerIdentifier(obj):
	HDno=0
	bayerName=None
	r=Simbad.query_objectids(obj)
	d={'HDno':0,'bayerName':''}
	
	try:
		for id in r:
			name=id['ID']
			#print 'name=',name
			if name.startswith('HD '):
				d['HDno']=int(name.split()[1])
				break

		for id in r:
			name=id['ID']
			if name.startswith('* '):
				d['bayerName']=name[2:].strip()
				break

	except:
		print("Except getHD_and_BayerIdentifier ")
	return d
	

def getVizier():
	v=Vizier()
	#"NOMAD", "UCAC","II/237"
	result = v.query_object("omi and",catalog=["II/237"])
	#print result
	for r in result:
		print(r)

def getsimbadMesurement(obj):
#	print Simbad.list_votable_fields()
#	print "********"
	s=Simbad()	
#	print s.get_votable_fields()

#	print "add VO field"
	s.add_votable_fields('otype(V)','sptype','mk','flux(V)','flux(B)','flux(R)','flux(H)','flux(K)','rv_value')
#	s.add_votable_fields('otype','sptype','mk','flux(V)','flux(B)','flux(R)','flux(H)','flux(K)','rv_value')
#	print s.get_votable_fields()

	r=s.query_object(obj)
	#print r
	#print "**************************************************"
	#print r.keys()
	

	d={}  # dictionnaire avec les informations du cds

	for key in ['RA','DEC']:
		try:
			d[key]=str(r[key]).split('\n')[3]
		except:
			d[key]=None;

	if d['RA']==None:	# on n a pas trouve les coords.. objet inconnus du CDS
		return {}

	# renome RA et DEC  en alpha delta,  car DEC mot reserve en SQL
	d['alpha']=d.pop('RA')
	d['delta']=d.pop('DEC')
		
	for key in ['FLUX_V','FLUX_B','FLUX_R','FLUX_K','FLUX_H','RV_VALUE']:
		try:
			d[key]=float(str(r[key]).split('\n')[3])
		except:
			d[key]=None;
			
	
	
	for key in ['SP_TYPE','MK_Spectral_type','OTYPE_V','MAIN_ID','SP_QUAL']:
		try:
			d[key]=str(r[key]).split('\n')[2].strip()
		except:
			d[key]=None

	if d['MAIN_ID'].startswith('* '):
		d['MAIN_ID']=d['MAIN_ID'][2:]
			
	return d
	
def testget(obj):
	print("obj=",obj, end=' ')
	print(" Coord:",getCoord(obj), end=' ')
	print(" HD,bayer=",getHD_and_BayerIdentifier(obj))

def test_cds():
	print("getSimbad:",getsimbadMesurement("del cep"))
	#print "getSimbad:",getsimbadMesurement("Mss1")
	testget("del cas")
	#testget("omi and")
	#testget("BD+56 452")
	#testget("HD13506")
