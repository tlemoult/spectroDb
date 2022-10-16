#!/bin/bash
echo startup observatory

cd ../python/
python startupObs.py

indiserver -v indi_lx200ap  indi_atik_ccd indi_asi_ccd

