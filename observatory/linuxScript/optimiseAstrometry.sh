#!/bin/bash

#ALPY + ALPY + ATIK314 bin 1x1
python3 fits_crop_all.py  200 100 800 800 ./ChampCassipee.fits
solve-field --downsample 4 --tweak-order 2 --scale-units arcsecperpix --scale-low 1.3 --scale-high 1.6 ./ChampCassipee_c.fits


#eShell + RC360 + ATIK314L bin 2x2

# with approximated coordinate
solve-field --ra 281.68 --dec 52.99 --radius 1 --downsample 2 --tweak-order 2 --scale-units arcsecperpix --scale-low 1 --scale-high 1.2 --continue ./FIELD-1.fits 


# with approximated coordinate, no additionnal binning
solve-field --ra 281.68 --dec 52.99 --radius 1 --downsample 1 --tweak-order 2 --scale-units arcsecperpix --scale-low 1 --scale-high 1.2 --continue ./FIELD-1.fits 


#          downsample2  downsample1   approx
#f1         Failed            OK          OK
#f2         2,48s           4,18s       1,22s
#f3         2,93s           4,50s
#f4         failed          failed     failed
#f5         1,48s			5.78s      
#f6			failed			 108s		3.53s
#f7         failed          2.36s     
#f8         1,35s           2.40s
#f9         2.20s           5.14s
#f10        1.24s           1.54s
#f11        1.99s           16s         1.24s


