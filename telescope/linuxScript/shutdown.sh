#!/bin/bash
echo startup observatory

cd ../python/
python  shutdownObs.py 

killall indiserver python


