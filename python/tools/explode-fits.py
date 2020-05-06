import sys,os
from os import walk
import urllib.request, urllib.parse, urllib.error,glob
import pyfits
from astropy.time import Time
import zipfile

import lib.explodeFits as expFits

#########
# main  #
#########
if len(sys.argv)==1:  # pas d argument
	print("prend un argument: repertoire de travail")	
	exit()
else:
	for (dirpath, dirnames, filenames) in walk(sys.argv[1]):
		for f in filenames:
			if f.endswith('.fits') or f.endswith('.fit'):

				(files,newBaseName)=expFits.explodeFits(dirpath,dirpath,f)
				if files!=[]:
					with zipfile.ZipFile(dirpath+'/'+newBaseName+'.zip','w') as myzip:
						for f in files:
							myzip.write(dirpath+'/'+f)

