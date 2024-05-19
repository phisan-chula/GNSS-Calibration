#!/bin/sh

set -x 
rm CACHE/RockArt_Baseline.gpkg
python3 GNSS_Planning.py
cp CACHE/RockArt_Baseline.gpkg /mnt/c/Users/User/Downloads/.
