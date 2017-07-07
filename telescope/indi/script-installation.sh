#Note
# teste avec INDI Library 1.1.0
# ne fonctionne pas avec INDI Library 1.4.1

# si besoin, pour virer paquet et repository trop recent de indilib:
# sudo apt-get install ppa-purge
# sudo ppa-purge ppa:mutlaqja/ppa


#installation du wrapper python indi
sudo apt-get install subversion libindi-dev python-dev swig cmake
pip install -i https://testpypi.python.org/pypi pyindi-client

#Installation of PHD2, on ubuntu
sudo add-apt-repository ppa:pch/phd2
sudo apt-get update
sudo apt-get install phd2

# run indi server
indiserver -vv indi_simulator_ccd

# run test
svn co svn://svn.code.sf.net/p/pyindi-client/code/trunk/swig-indi/swig-indi-python/
cd swig-indi-python
python test-indiclient.py


#run real sitation
#   Monut Astrophysics,  camera= atik

indiserver   indi_atik_ccd indi_lx200ap



