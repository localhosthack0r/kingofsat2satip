#!/bin/bash

# configure SATIP server name/IP address, here
SERVER="newslave"
#SERVER="192.168.178.42"

# cleanup old files
rm *.m3u
rm pos*

# download PHP files from kingofsat
wget https://de.kingofsat.net/pos-19.2E
wget https://de.kingofsat.net/pos-28.2E
wget https://de.kingofsat.net/pos-23.5E
wget https://de.kingofsat.net/pos-13E

# call python script to extract channel information from php files and generate m3u files
# the number at the end of the call is the satip src parameter (diseqc position)
python getchannels.py $SERVER pos-19.2E 1
python getchannels.py $SERVER pos-28.2E 2
python getchannels.py $SERVER pos-23.5E 3
python getchannels.py $SERVER pos-13E 4

# merge all m3u files together
cat *.m3u > allChannels.m3u
