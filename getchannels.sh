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
wget https://de.kingofsat.net/pos-9E
wget https://de.kingofsat.net/pos-7E
wget https://de.kingofsat.net/pos-0.8W

# call python script to extract channel information from php files and generate m3u files
# the number at the end of the call is the satip src parameter (diseqc position)
python getchannels.py $SERVER pos-19.2E 1
python getchannels.py $SERVER pos-28.2E 2
python getchannels.py $SERVER pos-23.5E 3
python getchannels.py $SERVER pos-13E 4
python getchannels.py $SERVER pos-9E 5
python getchannels.py $SERVER pos-7E 5
python getchannels.py $SERVER pos-0.8W 7

# merge all m3u files together
cat *.m3u > allChannels.m3u
