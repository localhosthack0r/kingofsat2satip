#!/bin/bash

rm *.php
rm *.m3u

wget https://de.kingofsat.net/pos-19.2E.php
python getchannels.py pos-19.2E.php 1

wget https://de.kingofsat.net/pos-28.2E.php
python getchannels.py pos-28.2E.php 2

wget https://de.kingofsat.net/pos-23.5E.php
python getchannels.py pos-23.5E.php 3


wget https://de.kingofsat.net/pos-13E.php
python getchannels.py pos-13E.php 4

cat *.m3u > allChannels.m3u

