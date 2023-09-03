#!/bin/bash
echo shutdown observatory

cd ../indi/
python  shutdownObs.py 

killall indiserver python


