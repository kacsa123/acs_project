import argparse
import csv
import json
#import numpy as np
import sys
from decimal import *




def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', dest='filename', required=True, help="csv file to read")
    parser.add_argument('--out', dest='out', required=True, help="file to write to")

    args = parser.parse_args(args)

    f = open(args.filename, "r")
    out = open(args.out, "w")
    
    flows = {}
	
    for row in f:
        fields = row.split(",")
        packet = fields[6]
        if not care(packet):
            continue
        
        port1 = packet[68:72]
        port2 = packet[72:76]
        id = min(port1,port2) + max(port1,port2)
        
        
        #if not checkSYN(packet):
                #print(packet)
        #    flows[id][2] = fields[5]
                #print(str(flows[id][0] + 1) + "," + flows[id][1] + "," + fields[5] + "," + id, file=out)
                #del flows[id]
            #else:
            #    print("FIN without prev " + packet)
        
        if checkSYN(packet):
            if id in flows:
                 if flows[id][3] == 2:
                     print(str(flows[id][0]) + "," + flows[id][1] + "," + flows[id][2] + "," + str(flows[id][4]) + "," + id, file=out)
                     del flows[id]
                 else:
                     flows[id][3] = 2
                #    print("Missing FIN "+str(flows[id][0] + 1) + "," + flows[id][1] + "," + id)
            if id not in flows:
                flows[id] = [0, fields[5], "", 1, int(fields[2])+4]
            flows[id][0] = flows[id][0] + 1
        else:
            if id in flows:
                flows[id][0] = flows[id][0] + 1
                flows[id][2] = fields[5]
                flows[id][4] = flows[id][4] + int(fields[2])+4
            #else:
                    #print("Packet without SYN " + packet + " " + fields[5])
                    #flows[id] = [1, fields[5]]
                
    for k,v in flows.items():
        print(str(v[0]) + "," + v[1] + "," + v[2] + "," + str(v[4]) + "," + k, file=out)
        #print(str(v[0]) + "," + v[1] + ",nan," + k, file=out)

def checkFIN(packet):
    # RST or FIN
	# both in last 4 bit of flags
    flags = bin(int(packet[95], 16))[2:].zfill(4)
    return (flags[1] == '1') or (flags[3] == '1')

def checkSYN(packet):
    # SYN
    # last 4 bit of flags
    flags = bin(int(packet[95], 16))[2:].zfill(4)
    return (flags[2] == '1')

def care(packet):
    # TODO: don't hardcode ip addresses
    return (packet[60:68] == "c0a80007" and packet[52:60] == "c0a80009") or (packet[60:68] == "c0a80009" and packet[52:60] == "c0a80007")


if __name__ == "__main__":
    main(sys.argv[1:])
