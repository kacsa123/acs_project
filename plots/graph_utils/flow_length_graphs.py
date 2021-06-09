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
                 #("../memcached/2_machines/swop_baseline_10Gb/flow_sizes.csv","Memcached, no cross traffic", "solid", "C0"),
                 #("../memcached/2_machines/poisson_1025b_0.3pps_moongen_10Gb/flow_sizes.csv","Memcached, Poisson cross traffic", (0, (4,2)), "C1"),
                 ("../apache/2_machines/const_trident_10Gb/flow_sizes_arista2.csv","Apache, Trident cross traffic, to client", "solid", "C0"),
                 #("../apache/2_machines/CBR_1025b_0.3pps_moongen_10Gb/1_moongen_arista2_flow_sizes.csv","Apache, 1 CBR cross traffic, to client", "solid", "C0"),
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/1_moongen_arista2_flow_sizes.csv","Apache, 1 Poisson cross traffic, to client", "solid", "C1"),
                 #("../apache/2_machines/CBR_1025b_0.3pps_moongen_10Gb/fct_07_server_arista2.csv","Apache, 2 CBR cross traffic, to client", "solid", "C2"),
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/fct_07_server_arista2.csv","Apache, 2 Poisson cross traffic, to client", "solid", "C3"),
                 ("../apache/2_machines/swop_baseline_10Gb/fct_07_server_arista2.csv","Apache, no cross traffic", "dashed", "#000000"),
                 #("../apache/2_machines/CBR_1025b_0.3pps_moongen_10Gb/bursts_200000ns.csv","Apache, to client, 200000 ns", "dashed", "C0"),
                 #("../memcached/2_machines/CBR_1025b_0.3pps_moongen_10Gb/flow_sizes.csv","Memcached, CBR cross traffic", (0, (5, 2, 1, 2)), "C2"),
                 #("../apache/2_machines/baseline_10Gb/fct_07_client.csv","Apache, no cross traffic (07 client)", "dashed", "C3"),
           
                 #("../apache/2_machines/swop_CBR_1025_0.3Mpps_10Gb/bursts_200000ns.csv","Apache, to server, 200000 ns", "dashed", "C1")
                 ]
    data_list = []
    
    for file in file_list:
        f = open(file[0], "r")

        data = get_flows(f)
        
        # data, label, style, colour
        data_list.append((data, file[1], file[2], file[3]))
    
    print("Make plot")
    
    plot_bursts(data_list)
        


  
def plot_bursts(data_list):

   
         
    plt.figure(1)
    plt.tight_layout()
    
    
    for data in data_list:
        print(max(data[0][0]))
        n,bins, patches = plt.hist(data[0][0], weights=data[0][1], bins=np.linspace(0.0005, 0.01, 2000),
                                   density=True, cumulative=True, histtype='step', label=data[1], linestyle=data[2], color=data[3], linewidth=2)
        patches[0].set_xy(patches[0].get_xy()[:-1])
    

    plt.xlabel("Flow length (s)")
    plt.ylabel("CDF")

    # Set legend below the graph
    ax = plt.gca()
    #ax.set_xscale('log')
    lgd = ax.legend(loc='lower right', ncol=1)
    #lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    
    #minor_ticks = np.arange(0, 54001, 1000)
    #ax.set_xticks(minor_ticks, minor=True)
    #plt.minorticks_on()
    #plt.grid(which='minor', linestyle='--')
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
    #ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    #plt.xlim(0.001, 0.01)
    ax.set_axisbelow(True)
    plt.grid()
    plt.rcParams["svg.fonttype"] = 'none'

    plt.savefig("all_cdf.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')
    

    
def get_flows(f):
    print("get flow lengths")

    data = []
    weights = []    
    for row in f:
        fields = row.split(",")
        if fields[2] != "":
            data.append(float(fields[2]) - float(fields[1]))
            #data.append(float(fields[3])/1000000)
            weights.append(int(fields[0]))
    return (data, weights)
        #data.append(float(row))
    #return data

if __name__ == "__main__":
    main()