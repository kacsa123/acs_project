import sys
import argparse
import matplotlib
matplotlib.use('Agg')
from decimal import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from math import sqrt

SPINE_COLOUR = 'gray'

# Delays: list of delays in picoseconds
def plot_delays(all_delays, label, title, outfile, dir):
    bins = 100
    delays = [x for (x,y,z) in all_delays if (dir == z)]
    packet_len = [y for (x,y,z) in all_delays if (dir == z)]
    if len(delays) == 0:
        return

    #min_lim = min(delays)
    #max_lim = max(delays)
    print("min len: " + str(min(packet_len)))
    print("max len: " + str(max(packet_len)))
    #bins = np.linspace(min_lim, max_lim, 1000)
    plt.figure(dir)
    plt.hist(packet_len, bins=bins, label=label)
    plt.title(label)
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    filename = outfile + "_packet_sizes.svg"
    plt.savefig(filename)

    plt.figure(str(dir) + "heat")
    plt.title(label)
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("Delays in picoseconds")
    
    cmap = plt.cm.plasma
    #cmap = plt.cm.RdYlGn
    y_min = min(all_delays)[0]-100000
    y_max = max(all_delays)[0]+100000
    x_min = min(all_delays, key = lambda t: t[1])[1]-1
    x_max = max(all_delays, key = lambda t: t[1])[1]+1
    print("y: " + str(y_min) + " " + str(y_max))
    plt.ylim(y_min, y_max)
    plt.hist2d(packet_len, delays, bins=100, cmap=cmap, norm=matplotlib.colors.LogNorm(vmin=2), range=[[x_min, x_max], [y_min, y_max]])
    cb = plt.colorbar()
    cb.set_label('Number of packets')
    # Set legend below the graph
    ax = plt.gca()
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    #filename = title + "_delays_ps_cdf.svg"
    filename = outfile + "_delays_by_packet_size.svg"
    plt.savefig(filename)


# File format is as follows:
# A line consists of:
# delay ns, delay ps, n.o. matches, _, capture time (s.ps), capture time (s.ns), length, data, -->, _, time (s.ps), time (s.ns), length
def extract_delays(file, limit=-1):
    delays = []
    bad = 0
    very_bad = 0
    for line in file:
        items = line.split(",")
        if items[2] != "1":
            continue
        if abs(int(items[0])) > 10000000:
            very_bad = very_bad + 1
            continue
        if limit != -1 and abs(int(items[1])) > limit:
            bad = bad + 1
            continue
        if (int(items[1]) > 0):
            delays.append((int(items[1]), int(items[6]), 1))
        else:
            delays.append((abs(int(items[1])), int(items[6]), -1))
    print("very bad: " + str(very_bad))
    print("above limit: " + str(bad) + " limit: " + str(limit) + "ps")
    return delays

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', dest='filename', required=True, help="file to plot")
    parser.add_argument('--label', dest='label', default=" ", help="label for plot")
    parser.add_argument('--title', dest='title', required=True, help="title of plot")
    parser.add_argument('--outfile', dest='savefile', required=True, help="name of output file")
    parser.add_argument('--limit', dest='limit', default="-1", help="limit in ps. Remove all packets with higher delays")
    args = parser.parse_args(args)
    delays = []
    f = open(args.filename, "r")
    delays = extract_delays(f, int(args.limit))
    print("Make plot for " + args.filename)
    plot_delays(delays, args.label, args.title + " to client", args.savefile + "_to_client", 1)
    print("Make second plot for " + args.filename)
    plot_delays(delays, args.label, args.title + " to server", args.savefile + "_to_server",-1)

if __name__ == "__main__":
    main(sys.argv[1:])
