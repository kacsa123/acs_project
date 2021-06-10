#!/bin/bash

EXPCAP_DIR=$1

if [[ $# -ne 1 ]]; then
        echo "Usage $0 <directory of expcap files>"
        exit 1
fi

pushd ${EXPCAP_DIR}
for i in *.bz2; do
    [ -f "$i" ] || break
    echo "unzipping $i"
    sudo time lbzip2 -dk ${i}
done

for i in *.expcap; do
    [ -f "$i" ] || break
    echo "parsing $i"
    echo "${i%%_*}.csv"
    sudo time ~/exact-capture/bin/exact-pcap-parse -i ${i} -c ${i%%_*}.csv -f expcap &
done
wait
for i in *.expcap; do
    [ -f "$i" ] || break
    sudo rm ${i}
done

popd
