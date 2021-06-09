import argparse
import csv
import json
import numpy as np
import sys
import matplotlib
import math
matplotlib.use('Agg')
from decimal import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

class Data:
    pass
# medians = [] <- 4 elems
# data = [[]] <- 4x8 elems



def main():    
    
    print("Make plot")
    
    data_files = [["apache_to_server_baseline.csv", "1_apache_to_server_cbr_7_5.csv", "1_apache_to_server_poisson_7_5.csv", "apache_to_server_cbr_7_5.csv", "apache_to_server_poisson_7_5.csv"],
                  ["dns_10Gb.csv", "1_dns_to_server_cbr_7_5.csv", "1_dns_to_server_poisson_7_5.csv", "dns_to_server_cbr_7_5.csv", "dns_to_server_poisson_7_5.csv"],
                  ["memcached_10Gb.csv", "1_memcached_to_server_cbr_7_5.csv", "1_memcached_to_server_poisson_7_5.csv", "memcached_to_server_cbr_7_5.csv", "memcached_to_server_poisson_7_5.csv"],
                  ["tensorflow_10Gb.csv", "1_tensorflow_to_server_cbr_7_5.csv", "1_tensorflow_to_server_poisson_7_5.csv", "tensorflow_to_server_cbr_7_5.csv", "tensorflow_to_server_poisson_7_5.csv"]
                 ]
    data = []
    for data_set in data_files:
        benchmark_data = []
        for file in data_set:
            benchmark_data.append(get_data(file))
        data.append(benchmark_data)
    
    plot(data)
    
    #plot([[ [10000.0, 20000.0, 90000.0], [20000.0, 200.0, 40000.0], [15000.0, 1000.0, 20001.0] ], [[18000, 10000, 2001], [12500, 15000, np.nan], [21000, 3000, 33333]] ])


def plot(datas):    
    
    
    
    plt.figure(1)
    plt.tight_layout()
    c = ["red", "green"]
    label = ["Apache", "DNS", "Memcached", "Tensorflow"]
    i = 0
    for data in datas:
        print(data)
        #print(data.shape)
        #print(data.ndim)
        max_mean = max(np.nanmean(data, axis=1))
        print(max_mean)
        normed_data = [[ d/max_mean for d in x] for x in data ]
        print(normed_data)
        stddevs = np.nanstd(normed_data, axis=1)
        means = np.nanmean(normed_data, axis=1)
        plt.errorbar(["No cross traffic", "1 CBR", "1 Poisson", "2 CBR", "2 Poisson"], means, yerr=stddevs, capsize=10, marker='s',
                    label=label[i])
        #plt.boxplot(normed_data, labels = ["10Gb/s", "10Gb/s, trident1", "5Gb/s", "5Gb/s, trident1", "5Gb/s, trident2"],
        #    capprops=dict(color=c[i]),
        #    whiskerprops=dict(color=c[i]),
        #    medianprops=dict(color=c[i]),)
        i += 1

    plt.ylabel("Normalised performance")
    # Set legend below the graph
    ax = plt.gca()
    lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    plt.rcParams['svg.fonttype'] = 'none'
    plt.savefig("test.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')
    
    
    
def get_data(file):
    data = []
    f = open(file, "r")
    for row in f:
        fields = row.split(",")
        #print(str(float(fields[2])*1000000000) + " " + str(fields[1]))
        if "tensorflow" in file:
            data.append(1/float(fields[0]))
        else:
            data.append(float(fields[0]))
    
    padded_data = np.pad(data, (0, 10 - len(data)), 'constant', constant_values=np.nan)
    return padded_data

if __name__ == "__main__":
    main()