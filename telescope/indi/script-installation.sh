




sudo apt-get install subversion libindi-dev python-dev swig cmake

# download SVN repo
svn co svn://svn.code.sf.net/p/pyindi-client/code/trunk/swig-indi/swig-indi-python/

# update FindINDI.cmake
wget http://sourceforge.net/p/indi/code/HEAD/tree/trunk/cmake_modules/FindINDI.cmake?format=raw -O swig-indi-python/cmake_modules/FindINDI.cmake

# change to build directory
mkdir libindipython
cd libindipython

# execute cmake with python2.7 path
cmake -D PYTHON_LIBRARY=/usr/lib/python2.7/config-x86_64-linux-gnu/libpython2.7.so -D PYTHON_INCLUDE_DIR=/usr/include/python2.7/ ../swig-indi-python/

# build and install
make
sudo make install

####################################
#
###########################################

#autre solution
sudo apt-get install subversion libindi-dev python-dev swig cmake
# download SVN repo
svn co svn://svn.code.sf.net/p/pyindi-client/code/trunk/swig-indi/swig-indi-python/

pip install -i https://testpypi.python.org/pypi pyindi-client

# run indi server
indiserver -v indi_simulator_ccd


# run test
cd swig-indi-python
python test-indiclient.py

