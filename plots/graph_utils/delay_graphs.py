import argparse
import csv
import json
import numpy as np
from numpy import convolve, cumsum, histogram, linspace
import sys
import matplotlib
matplotlib.use('Agg')
from decimal import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator



def main():
     
    file_list = [
                 #("../apache/2_machines/baseline_10Gb/nf07_switch2_delays.csv","Apache 10Gb/s", 53.9 , "solid", "C0"),
                 #("../apache/2_machines/baseline_10Gb/nf07_switch1_delays.csv","Apache 10Gb/s - switch 1", 18.2, "dashed", "C0"),
                 #("../apache/2_machines/baseline_10Gb/switch1_switch2_delays.csv","Apache 10Gb/s - switch 2", 35.7, (0, (5, 5, 1, 5)), "C0"),
                 #("../apache/2_machines/baseline_5Gb/nf07_switch1_delays.csv", "Apache 5Gb/s"),
                 #("../tensorflow/2_machines/const_trident_10Gb/nf07_switch1_delays.csv","Apache 10Gb/s, trident1 - switch 1", 18.2, "solid", "C1"),
                 #("../tensorflow/2_machines/const_trident_10Gb/switch1_switch2_delays.csv","Apache 10Gb/s, trident1 - switch 2", 35.7, "solid", "C2"),
                 #("../tensorflow/2_machines/const_trident_10Gb/nf07_switch2_delays.csv","Apache 10Gb/s, trident1 - total delay", 53.9 , "solid", "C0"),
                 
               
                 
                 #("../apache/2_machines/const_trident_10Gb/nf07_switch2_delays.csv","Apache to client - combined",  53.9 , "solid", "C0"),
                 #("../apache/2_machines/const_trident_10Gb/nf07_switch1_delays.csv","Apache to client - switch 1", 18.2, "dashed", "C0"),
                 #("../apache/2_machines/const_trident_10Gb/switch1_switch2_delays.csv","Apache to client - switch 2", 35.7, (0, (5, 5, 1, 5)), "C0"),
                 #("../apache/2_machines/const_trident_10Gb/switch1_switch2_delays.csv","Apache to client - switch 2", 35.7, (0, (5, 5, 1, 5)), "C0"),
                 
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/nf07_switch2.csv","Apache, Poisson Moongen - total delay",  53.9 , "solid", "C0"),
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/nf07_switch1.csv","Apache, Poisson Moongen - switch 1", 18.2, "solid", "C1"),
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/switch1_switch2.csv","Apache, Poisson Moongen - switch 2", 35.7, "solid", "C2"),
                 
                 #("../apache/2_machines/poisson_1025b_2.5Gb_moongen_10Gb/nf07_switch2.csv","Apache to server - combined",  53.9 , "solid", "C1"),
                 #("../apache/2_machines/poisson_1025b_2.5Gb_moongen_10Gb/nf07_switch1.csv","Apache to server - switch 1", 18.2, "dashed", "C1"),
                 #("../apache/2_machines/poisson_1025b_2.5Gb_moongen_10Gb/switch1_switch2.csv","Apache to server - switch 2", 35.7, "dotted", "C1"),
                 
                 
                 ("../apache/2_machines/const_trident_10Gb/nf07_switch1_delays.csv","Apache - switch 1", 18.2, "solid", "C1"),
                 ("../apache/2_machines/const_trident_10Gb/switch1_switch2_delays.csv","Apache - switch 2", 35.7, "solid", "C2"),
                 ("../apache/2_machines/const_trident_10Gb/nf07_switch2_delays.csv","Apache - total delay",  53.9 , "solid", "C0"),

                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/switch1_switch2.csv","Apache, Poisson traffic - switch 2", 35.7, (0, (5, 1, 1, 1)), "C1"),
                 
                 
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/nf07_switch1.csv","Apache, CBR Moongen - switch 1", 18.2, "solid", "C1"),
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/switch1_switch2.csv","Apache, CBR Moongen - switch 2", 35.7, "solid", "C2"),
                 #("../apache/2_machines/poisson_1025b_0.3pps_moongen_10Gb/nf07_switch2.csv","Apache, CBR Moongen - total delay",  53.9 , "solid", "C0"),
                 
                 
                 #("../memcached/2_machines/swop_CBR_1025_0.3Mpps_10Gb/nf07_switch1_filtered.csv","Memcached to server - switch 1", 18.2, "dashed", "C1"),
                 #("../memcached/2_machines/swop_CBR_1025_0.3Mpps_10Gb/switch1_switch2_filtered.csv","Memcached to server - switch 2", 35.7, (0, (5, 5, 1, 5)), "C1"),
                 #("../memcached/2_machines/swop_CBR_1025_0.3Mpps_10Gb/nf07_switch2_filtered.csv","Memcached to server - combined",  53.9 , "solid", "C1"),
            
                 
                 #("../memcached/2_machines/poisson_1025b_0.3pps_moongen_10Gb/nf07_switch1_filtered.csv","Memcached 10Gb/s, Poisson Moongen - switch 1", 18.2, "dashed", "C1"),
                 #("../memcached/2_machines/poisson_1025b_0.3pps_moongen_10Gb/switch1_switch2_filtered.csv","Memcached 10Gb/s, Poisson Moongen - switch 2", 35.7, (0, (5, 5, 1, 5)), "C1"),
                 #("../memcached/2_machines/poisson_1025b_0.3pps_moongen_10Gb/nf07_switch2_filtered.csv","Memcached 10Gb/s, Poisson Moongen - combined",  53.9 , "solid", "C1"),
                 
                 #("../memcached/2_machines/swop_poisson_1025_0.3Mpps_10Gb/nf07_switch1_filtered.csv","Memcached 10Gb/s, Poisson Moongen - switch 1", 18.2, "dashed", "C1"),
                 #("../memcached/2_machines/swop_poisson_1025_0.3Mpps_10Gb/switch1_switch2_filtered.csv","Memcached 10Gb/s, Poisson Moongen - switch 2", 35.7, (0, (5, 5, 1, 5)), "C1"),
                 #("../memcached/2_machines/swop_poisson_1025_0.3Mpps_10Gb/nf07_switch2_filtered.csv","Memcached 10Gb/s, Poisson Moongen - combined",  53.9 , "solid", "C1"),
                 
                 
                 #("../tensorflow/2_machines/iat_to_server/nf07_ipg.csv","Tensorflow - to server", 0, "dashed", "C0"),
                 #("../tensorflow/2_machines/iat_to_client/nf07_ipg.csv","Tensorflow - to client", 0, "solid", "C0"),
                 #("../memcached/2_machines/iat_to_server/nf07_ipg.csv","Memcached - to server", 0, "dashed", "C1"),
                 #("../memcached/2_machines/iat_to_client/nf07_ipg.csv","Memcached - to client", 0, "solid", "C1"),
                 #("../apache/2_machines/iat_to_server/nf07_ipg.csv","Apache - to server", 0, "dashed", "C2"),
                 #("../apache/2_machines/iat_to_client/nf07_ipg.csv","Apache - to client", 0, "solid", "C2"),
                 #("../dns/2_machines/iat_to_server/nf07_iat.csv","DNS - to server", 0, "dashed", "C3"),
                 #("../dns/2_machines/iat_to_client/nf07_iat.csv","DNS - to client", 0, "solid", "C3"),
                 #("../dns/2_machines/iat_to_server/nf07_ipg.csv","DNS - to server", 0, "dashed", "C3"),
                 #("../dns/2_machines/iat_to_client/nf07_ipg.csv","DNS - to client", 0, "solid", "C3"),
                 
                 
                 #("../tensorflow/2_machines/CBR_var_size_1025b_0.3pps_moongen_10Gb/nf07_switch1.csv","Tensorflow, var. size CBR - switch 1", 18.2, (0, (4,2)), "C0"),
                 #("../tensorflow/2_machines/CBR_var_size_1025b_0.3pps_moongen_10Gb/switch1_switch2.csv","Tensorflow, var. size CBR - switch 2", 35.7, (0, (5, 1, 1, 1)), "C0"),
                 #("../tensorflow/2_machines/CBR_var_size_1025b_0.3pps_moongen_10Gb/nf07_switch2.csv","Tensorflow, var. size CBR - total delay", 53.9, "solid", "C0"),
                 
                 #("../tensorflow/2_machines/CBR_1025b_2.5Gb_moongen_10Gb/nf07_switch1.csv","Tensorflow, CBR - switch 1", 18.2, (0, (4,2)), "C2"),
                 #("../tensorflow/2_machines/CBR_1025b_2.5Gb_moongen_10Gb/switch1_switch2.csv","Tensorflow, CBR - switch 2", 35.7, (0, (5, 1, 1, 1)), "C2"),
                 #("../tensorflow/2_machines/CBR_1025b_2.5Gb_moongen_10Gb/nf07_switch2.csv","Tensorflow, CBR - total delay", 53.9, "solid", "C2"),
                 
                 #("../tensorflow/2_machines/poisson_1025_0.9Mpps_10Gb/nf07_switch1.csv","Tensorflow, Poisson - switch 1", 18.2, "dashed", "#000000"),
                 #("../tensorflow/2_machines/poisson_1025_0.9Mpps_10Gb/switch1_switch2.csv","Tensorflow, Poisson - switch 2", 35.7, (0, (5, 2, 1, 2)), "#000000"),
                 #("../tensorflow/2_machines/poisson_1025_0.9Mpps_10Gb/nf07_switch2.csv","Tensorflow, Poisson - total delay", 53.9, "dashed", "#000000"),
                 
                 
                 #("../tensorflow/2_machines/swop_poisson_1025_0.3Mpps_10Gb/nf07_switch2.csv","Tensorflow to client, Poisson Moongen", 53.9, "dashed", "C1"),
                 #("../tensorflow/2_machines/baseline_10Gb/nf07_switch2_delays.csv","Tensorflow 10Gb/s", 53.9, "solid", "C3"),
                  #("../tensorflow/2_machines/baseline_10Gb/nf07_switch1_delays.csv","Tensorflow 10Gb/s - switch 1", 18.2, "dashed", "C3"),
                  #("../tensorflow/2_machines/baseline_10Gb/switch1_switch2_delays.csv","Tensorflow 10Gb/s - switch 2", 35.7, (0, (5, 5, 1, 5)), "C3"),
                 #("../tensorflow/2_machines/CBR_var_size_1025b_0.3pps_moongen_5Gb/nf07_switch1_delays.csv","Tensorflow 5Gb/s, Var. size CBR Moongen"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_4Mp_105b_CBR/nf07_switch1.csv", "Var. size CBR traffic, 2.5 Gb/s CBR cross traffic - switch 1"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_4Mp_105b_CBR/switch1_switch2.csv", "Var. size CBR traffic, 4 Gb/s CBR cross traffic - switch 2"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_4Mp_105b_CBR/nf07_switch2.csv", "Var. size CBR traffic - combined")
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_4Mp_2-5Mp_105b_CBR/nf07_switch1.csv", "Var. size CBR traffic, 4 Gb/s CBR cross traffic - switch 1"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_4Mp_2-5Mp_105b_CBR/switch1_switch2.csv", "Var. size CBR traffic, 2.5 Gb/s CBR cross traffic - switch 2"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_4Mp_2-5Mp_105b_CBR/nf07_switch2.csv", "Var. size CBR traffic - combined"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_105b_CBR_4Mp_105b_poisson/nf07_switch1.csv", "Var. size CBR traffic, 2.5 Gb/s CBR cross traffic - switch 1"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_105b_CBR_4Mp_105b_poisson/switch1_switch2.csv", "Var. size CBR traffic, 4 Gb/s poisson cross traffic - switch 2"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_105b_CBR_4Mp_105b_poisson/nf07_switch2.csv", "Var. size CBR traffic - total delay")
                 
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_105b_poisson/nf07_switch1.csv", "Var. size CBR traffic, 2.5 Gb/s Poisson cross traffic - switch 1",  18.2, "solid", "C1"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_105b_poisson/switch1_switch2.csv", "Var. size CBR traffic, 2.5 Gb/s Poisson cross traffic - switch 2",  35.7, "solid", "C2"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_4Mp_105b_CBR/nf07_switch2.csv", "2.5 Gb/s then 4 Gb/s CBR cross traffic", 53.9, "solid", "C0"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_4Mp_2-5Mp_105b_CBR/nf07_switch2.csv", "4 Gb/s then 2.5 Gb/s CBR cross traffic", 53.9, "solid", "C1"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_2-5Mp_4Mp_105b_poisson/07_switch2_delay.csv", "2.5 Gb/s then 4 Gb/s Poisson cross traffic", 53.9, (0, (4,2)), "C2"),
                 #("../moongen_moongen/4_machines/4Mp_130b_var_size_4Mp_2-5Mp_105b_poisson/07_switch2_delay.csv", "4 Gb/s then 2.5 Gb/s Poisson cross traffic", 53.9, (0, (4,2)), "C3"),
                 
                 ]
    data_list = []
    
    for file in file_list:
        f = open(file[0], "r")
        ftype = file[0].split(".")[-1]
        if ftype == "csv":
            data = get_delays(f)
        else:
            data = get_delays_json(f)
        
        # data, label, adj, style, colour
        data_list.append((data, file[1], file[2], file[3], file[4]))
    
    print("Make plot")
    
    plot_delays(data_list)
        


  
def plot_delays(data_list):

   
         
    plt.figure(1)
    #plt.figure(figsize=(2.5,2.5))
    plt.tight_layout()
    
    
    for data in data_list:
        data_adj = [x - data[2] for x in data[0][0]]
        print(data_adj[0])
        n,bins, patches = plt.hist(data_adj, bins=2000, weights=data[0][1], density=True, cumulative=True, histtype='step', label=data[1], linestyle=data[3], color=data[4], linewidth=1.5)
        patches[0].set_xy(patches[0].get_xy()[:-1])
    #n,bins, patches = plt.hist(list(data.keys()), bins=200, weights=list(data.values()), label="Measured delays for " + data_type + " packets")
    
    
    vals1 = [x - data_list[0][2] for x in data_list[0][0][0]]
    max1 = max(vals1)
    
    vals2 = [x - data_list[1][2] for x in data_list[1][0][0]]
    max2 = max(vals2)
    
    mul = max(max1, max2)/2000
    print(str(mul))
    bins = [x * mul for x in range(0, 2001)]
    pdf_1= histogram(vals1, weights=data_list[0][0][1], bins= bins)[0]
    pdf_2= histogram(vals2, weights=data_list[1][0][1], bins= bins)[0]
    print(str(len(pdf_1)))
    print(str(len(pdf_2)))
    c= convolve(pdf_1, pdf_2); #c= c/ c.sum()
    bins = [x * mul for x in range(0, len(c))]
    #print(str(bins))
    n,bins, patches = plt.hist(bins ,weights = c, bins = bins, density=True, cumulative=True,
                               histtype='step', label="Sum of switch 1 and switch 2 delay distributions", linestyle=(0, (4, 2)), color='#000000', linewidth=1.5)
    patches[0].set_xy(patches[0].get_xy()[:-1])
    
    #plt.title("Delays")
    #plt.xlabel("Packet size (bytes)")
    plt.xlabel("Delay (ns)")
    plt.ylabel("CDF")
    #plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    #ax.set_xscale('log')
    lgd = ax.legend(loc='lower right', ncol=1)
    #lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    
    
    #minor_ticks = [82, 132]
    #ax.set_xticks(minor_ticks)
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
        
    #ax.set_xlim(0, 10000)
    #ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    plt.rcParams["svg.fonttype"] = 'none'
    #filename = title + "_delays_ps_cdf.svg"
    #filename = title + "_delays_ps.svg"
    plt.savefig("all_cdf.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')
    
    
    
    
    plt.figure(2)
    plt.tight_layout()
    
    for data in data_list:
        #n,bins, patches = plt.hist(list(data[0].keys()), bins=1000, weights=list(data[0].values()), density=True, cumulative=True, histtype='step', label=data[1])
        #patches[0].set_xy(patches[0].get_xy()[:-1])
        data_adj = [x - data[2] for x in data[0][0]]
        n,bins, patches = plt.hist(data_adj, bins=1000, weights=data[0][1], density=True, histtype='step', label=data[1], linestyle=data[3], color=data[4])
    
    #plt.title("Delays")
    #plt.xlabel("Delay (ns)")
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    
    #ax.set_xscale('log')
    lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    # Limit y to 1
    ax.set_xlim(0, 125000)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    plt.rcParams["svg.fonttype"] = 'none'
    #filename = title + "_delays_ps_cdf.svg"
    #filename = title + "_delays_ps.svg"
    plt.savefig("all_hist.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')

    
def get_delays(f):
    print("get delays")
    #csv_reader = csv.reader(f, delimiter=',')
    #print("get delays")
    data = []
    weights = []
    for row in f:
        fields = row.split(",")
        #print(str(float(fields[2])*1000000000) + " " + str(fields[1]))
        #data[float(fields[2])*1000000000] = int(fields[1])
        if float(fields[2]) < 1:
            data.append(float(fields[2])*1000000000)
        else:
            data.append(float(fields[2]))
        weights.append(int(fields[1]))

    return (data, weights)

def get_delays_json(f):
    print("get delays json")
    all_data = json.load(f)
    values_list = all_data['data']['values']
    data = []
    weights = [] 
    for m in values_list:
        #print(str(m))
        data.append(m['diff_bucket_val']*1000000000)
        weights.append(m['count'])
    
    return (data, weights)


if __name__ == "__main__":
    main()