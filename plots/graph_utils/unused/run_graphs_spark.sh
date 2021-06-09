#!/bin/bash

EXPCAP_DIR=$1
APPLICATION=$2
SERVER_COUNT=$3
CLIENT_COUNT=$4

if [[ $# -ne 4 ]]; then
        echo "Usage $0 <directory of expcap files> <application name> <number of servers> <number of clients>"
        exit 1
fi

servers=($(grep -e ${APPLICATION}-server -e ${APPLICATION}-master ${EXPCAP_DIR}/MachineRoles | awk -M 'BEGIN { FS = "."; }
{
    printf "%s ", substr($4, 2, 2)
}'))

#servers=($(cat < temp.txt))

clients=($(grep -e ${APPLICATION}-client -e ${APPLICATION}-slave ${EXPCAP_DIR}/MachineRoles | awk -M 'BEGIN { FS = "."; }
{
    printf "%s ", substr($4, 2, 2) 
}'))


if [ ! -f  ${EXPCAP_DIR}/${servers[0]}_${clients[0]}_tcp_packets_match.csv ]; then
   
client_no=0
while (( client_no < CLIENT_COUNT )); do
    capture_machine=$(grep nf-server${clients[$client_no]} ~/graph_utils/capture_machines | awk -M '{print $2}' | tr -d ' ')
    echo "$capture_machine"
    echo "nf-server${clients[$client_no]}"
    if [ ! -f ${EXPCAP_DIR}/nf-server${clients[$client_no]}.expcap ]; then
        sudo time lbzip2 -dc ${EXPCAP_DIR}/nf-server${clients[$client_no]}.nf.cl.cam.ac.uk_captured_by_${capture_machine}.nf.cl.cam.ac.uk.expcap.bz2 | sudo tee ${EXPCAP_DIR}/nf-server${clients[$client_no]}.expcap > /dev/null
    fi
    client_no=$(( client_no + 1 ))
done

server_no=0
while (( server_no < SERVER_COUNT )); do
    capture_machine=$(grep nf-server${servers[$server_no]} ~/graph_utils/capture_machines | awk -M '{print $2}' | tr -d ' ')
    echo "$capture_machine"
    echo "nf-server${servers[$server_no]}"
    if [ ! -f ${EXPCAP_DIR}/nf-server${servers[$server_no]}.expcap ]; then
        sudo time lbzip2 -dc ${EXPCAP_DIR}/nf-server${servers[$server_no]}.nf.cl.cam.ac.uk_captured_by_${capture_machine}.nf.cl.cam.ac.uk.expcap.bz2 | sudo tee ${EXPCAP_DIR}/nf-server${servers[$server_no]}.expcap > /dev/null
    fi
    server_no=$(( server_no + 1 ))
done

#wait
fi


client_no=0
server_no=0
while (( server_no < SERVER_COUNT )); do
	while (( client_no < CLIENT_COUNT )); do
                
                if [ ! -d  ${EXPCAP_DIR}/${servers[$server_no]}_${clients[$client_no]}_match ]; then
                    if [ ! -f ${EXPCAP_DIR}/nf-server${servers[$server_no]}.csv ]; then
                         sudo time ~/exact-capture/bin/exact-pcap-parse -i ${EXPCAP_DIR}/nf-server${servers[$server_no]}.expcap -c ${EXPCAP_DIR}/nf-server${servers[$server_no]}.csv -f expcap
                    fi
                    if [ ! -f ${EXPCAP_DIR}/nf-server${clients[$client_no]}.csv ]; then
                         sudo time ~/exact-capture/bin/exact-pcap-parse -i ${EXPCAP_DIR}/nf-server${clients[$client_no]}.expcap -c ${EXPCAP_DIR}/nf-server${clients[$client_no]}.csv -f expcap
                    fi
                    pushd ~/spark
		    sudo /opt/spark/bin/spark-submit --driver-memory 16g /auto/homes/tpe23/spark/target/scala-2.12/match-packets_2.12-1.0.jar "${EXPCAP_DIR}/nf-server${servers[$server_no]}.csv" "${EXPCAP_DIR}/nf-server${clients[$client_no]}.csv" "${EXPCAP_DIR}/${servers[$server_no]}_${clients[$client_no]}_match"
                    popd
                fi
                
		time python3 ~/graph_utils/graph_utils/delays_spark.py --dir ${EXPCAP_DIR}/${servers[$server_no]}_${clients[$client_no]}_match --title "${APPLICATION} ${servers[$server_no]},  ${clients[$client_no]}" --outfile "${APPLICATION}_${servers[$server_no]}_${clients[$client_no]}_10000ns" --limit "10000"
		#time python3 ~/graph_utils/graph_utils/delays.py --file ${EXPCAP_DIR}/${servers[$server_no]}_${clients[$client_no]}_tcp_packets_match.csv --title "${APPLICATION} ${servers[$server_no]},  ${clients[$client_no]}" --outfile "${APPLICATION}_${servers[$server_no]}_${clients[$client_no]}_4000ns" --limit "4000000"
		#time python3 ~/graph_utils/graph_utils/delays_by_packet_size.py --file ${EXPCAP_DIR}/${servers[$server_no]}_${clients[$client_no]}_tcp_packets_match.csv --title "${APPLICATION} ${servers[$server_no]},  ${clients[$client_no]}" --outfile "${APPLICATION}_${servers[$server_no]}_${clients[$client_no]}_4000ns" --limit "4000000"
                # echo "${EXPCAP_DIR}/${servers[$server_no]}_${clients[$client_no]}"
		client_no=$(( client_no + 1 ))
	done
        sudo rm ${EXPCAP_DIR}/nf-server${servers[$server_no]}.expcap
        server_no=$(( server_no + 1 ))
done

while (( client_no < CLIENT_COUNT )); do
	sudo rm ${EXPCAP_DIR}/nf-server${clients[$client_no]}.expcap
done
