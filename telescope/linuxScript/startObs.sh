#!/bin/bash
echo startup observatory

cd ../python/
python startupObs.py

python gui-powerBox.py > /dev/null &
python gui-astrosib.py > /dev/null &

indiserver -p 7624 -v indi_lx200ap  indi_atik_ccd indi_asi_ccd indi_sx_ccd > /dev/null &



