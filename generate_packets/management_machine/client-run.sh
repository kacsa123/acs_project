#!/bin/bash
mkdir -p /data
pushd /root/jcw78/scripts/moongen/MoonGen/
{ sleep 90; killall -9 MoonGen; } &
sudo ./build/MoonGen ./examples/l3-unique-udp.lua 0 1 -t 10 > /data/moongen
#sudo ./moongen-simple start udp-test:0:1 > /data/moongen
popd
