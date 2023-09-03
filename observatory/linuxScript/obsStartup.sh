#!/bin/bash
echo startup observatory

cd ../indi/
python startupObs.py

cd ../gui/
python gui-powerBox.py > /dev/null &
python gui-astrosib.py > /dev/null &

indiserver -p 7624 -v indi_lx200ap  indi_asi_ccd  > /dev/null &



