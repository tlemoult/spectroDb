#Note
# teste avec INDI Library 1.1.0
# ne fonctionne pas avec INDI Library 1.4.1

# si besoin, pour virer paquet et repository trop recent de indilib:
# sudo apt-get install ppa-purge
# sudo ppa-purge ppa:mutlaqja/ppa


#installation de client indi, en python !
sudo apt-get install subversion libindi-dev python-dev swig cmake python-pip
pip install -i https://testpypi.python.org/pypi pyindi-client

# test python client
svn co svn://svn.code.sf.net/p/pyindi-client/code/trunk/swig-indi/swig-indi-python/
cd swig-indi-python
python test-indiclient.py


#Installation of PHD2, on ubuntu
sudo add-apt-repository ppa:pch/phd2
sudo apt-get update
sudo apt-get install phd2

# Installation kstars standart
sudo apt-get install kstars

#installation de kstars et ekos derniere version
sudo apt-add-repository ppa:mutlaqja/ppa
sudo apt-get update
sudo apt-get install kstars-bleeding

# run indi server
indiserver -vv indi_simulator_ccd

#Installation pour ccd simulator;  gsc
sudo apt-get install gsc

#####################################
#installation astrometry.net
#configuration, voir fichier /etc/astrometry.cfg
sudo apt-get install astrometry.net 
#pour les grands champ de 30 a 2000 acminutes
sudo apt-get install astrometry-data-2mass-08-19
Pour LISA+ATIK314+L130:  (prend 1.3Go)
sudo apt-get install astrometry-data-2mass-07 astrometry-data-2mass-06 astrometry-data-2mass-05
#pour les champ de 08-11 arcminutes
sudo apt-get install astrometry-data-2mass-04
#pour les champ de 5.6-08 arcminutes
sudo apt-get install astrometry-data-2mass-03

######################
# exemple astrometry
#resolution L130 + ST8
solve-field  --scale-units arcsecperpix -L 2.2 -H 2.3 M95-1.fits
#OK, avec 2mass-05
solve-field  --scale-units arcsecperpix -L 3.4 -H 3.6 L130-LISA-ATIK314-bin2.fits
# OK, avec 2mass-05
solve-field  --scale-units arcsecperpix -L 1.7 -H 1.90 L130-LISA-ATIK314.fits 
#resolution  RC360+eShell
solve-field  --scale-units arcsecperpix -L 1.2 -H 1.3 RC360eshel.fits
#resolution C14 + LISA
solve-field  --scale-units arcsecperpix -L 1.2 -H 1.3 C14-LISA.fits


############
# avec les image de INDI #
###########################
solve-field --no-verify --no-plots --no-fits2fits --downsample 2 --overwrite ./img/Light_001.fits

#champ L130 + ALPY + ATK314 bin1
solve-field --no-verify --no-plots --no-fits2fits --overwrite -L 0.9 -H 1.1 -u arcsecperpix FIELD-1.fits

#chercheur OHP, lodestar + TeleF135mm
solve-field --overwrite -L 2 -H 3  --downsample 3  ./finder/fix.FINDER-4.fits

