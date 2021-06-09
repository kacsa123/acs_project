import argparse
import csv
import json
import numpy as np
import sys
import matplotlib
matplotlib.use('Agg')
from decimal import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator



def main():
     
    file_list = [
                 ("../trident/test/run_2_constant_10_conn/bursts_100.csv","Trident, to server, 100 ns", "solid", "C0"),
                 #("../trident/test/run_2_constant_10_conn/bursts_800.csv","Trident, to server, 800 ns", "solid", "C1"),
                 ("../trident/test/run_2_constant_10_conn/bursts_1200.csv","Trident, to server, 1200 ns", "solid", "C2"),
                 #("../memcached/2_machines/CBR_1025b_0.3pps_moongen_10Gb/bursts_200000ns.csv","Apache, CBR cross traffic, to client, 200000 ns", "solid", "C0"),
                 #("../memcached/2_machines/swop_baseline_10Gb/bursts_200000ns.csv","Apache, no cross traffic, to client, 200000 ns", "solid", "C2"),
                 #("../apache/2_machines/CBR_1025b_0.3pps_moongen_10Gb/bursts_200000ns.csv","Apache, to client, 200000 ns", "dashed", "C0"),
                 #("../memcached/2_machines/swop_CBR_1025_0.3Mpps_10Gb/bursts_200000ns.csv","Apache, CBR cross traffic, to server, 200000 ns", "solid", "C1"),
                 #("../memcached/2_machines/baseline_10Gb/bursts_200000ns.csv","Apache, no cross traffic, to server, 200000 ns", "solid", "C3"),
                 #("../apache/2_machines/swop_CBR_1025_0.3Mpps_10Gb/bursts_200000ns.csv","Apache, to server, 200000 ns", "dashed", "C1")
                 ]
    data_list = []
    
    for file in file_list:
        f = open(file[0], "r")

        data = get_bursts(f)
        
        # data, label, style, colour
        data_list.append((data, file[1], file[2], file[3]))
    
    print("Make plot")
    
    plot_bursts(data_list)
        


  
def plot_bursts(data_list):

   
         
    plt.figure(1)
    plt.tight_layout()
    
    
    for data in data_list:
        #print(max(data[0]))
        n,bins, patches = plt.hist(data[0][0], weights=data[0][1], bins=1000, density=True, cumulative=True, histtype='step', label=data[1], linestyle=data[2], color=data[3], linewidth=1.5)
        patches[0].set_xy(patches[0].get_xy()[:-1])
    #n,bins, patches = plt.hist(list(data.keys()), bins=200, weights=list(data.values()), label="Measured delays for " + data_type + " packets")
    
    #plt.title("Delays")
    plt.xlabel("Burst length (no. packets)")
    plt.ylabel("CDF (packets)")
    #plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    #ax.set_xscale('log')
    lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    
    minor_ticks = [2]
    ax.set_xticks(minor_ticks, minor=True)
    #plt.minorticks_on()
    plt.grid(which='minor', linestyle='--')
    # Limit y to 1
    (ymin, ymax) = plt.ylim()
    if ymax > 1:
        plt.ylim(ymin, 1)
    (ymin, ymax) = plt.ylim()
    (xmin, xmax) = plt.xlim()
    if ymin < 0:
        plt.ylim(0, ymax)
    if xmin < 0:
        plt.xlim(0, xmax)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    plt.rcParams["svg.fonttype"] = 'none'
    #filename = title + "_delays_ps_cdf.svg"
    #filename = title + "_delays_ps.svg"
    plt.savefig("all_cdf.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')
    
    
    
    
    plt.figure(2)
    plt.tight_layout()
    
    for data in data_list:
        #print(max(data[0]))
        weights=[data[0][1][0]] + [1] * (len(data[0][0]) - 1)
        
        n,bins, patches = plt.hist(data[0][0], weights=weights, bins=1000, density=True, cumulative=True, histtype='step', label=data[1], linestyle=data[2], color=data[3], linewidth=1.5)
        patches[0].set_xy(patches[0].get_xy()[:-1])
    
    #plt.title("Delays")
    plt.xlabel("Burst length (no. packets)")
    plt.ylabel("CDF (bursts)")
    #plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    
    #ax.set_xscale('log')
    lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    # Limit y to 1
    minor_ticks = [2]
    ax.set_xticks(minor_ticks, minor=True)
    #plt.minorticks_on()
    plt.grid(which='minor', linestyle='--')
    
    (ymin, ymax) = plt.ylim()
    if ymax > 1:
        plt.ylim(ymin, 1)
    (ymin, ymax) = plt.ylim()
    (xmin, xmax) = plt.xlim()
    if ymin < 0:
        plt.ylim(0, ymax)
    if xmin < 0:
        plt.xlim(0, xmax)
    
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    plt.rcParams["svg.fonttype"] = 'none'
    #filename = title + "_delays_ps_cdf.svg"
    #filename = title + "_delays_ps.svg"
    plt.savefig("all_hist.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')

    
def get_bursts(f):
    print("get delays")
    #csv_reader = csv.reader(f, delimiter=',')
    #print("get delays")
    data = []
    weights = []    
    for row in f:
        fields = row.split(",")
        if fields[0] =="0":
            data.append(int(fields[1]))
            weights.append(int(fields[2]))
        else:
        #if int(fields[1]) < 500:
            data.append(int(fields[1]))
            weights.append(int(fields[1]))

    return (data, weights)


if __name__ == "__main__":
    main()