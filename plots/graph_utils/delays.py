import sys
import argparse
import matplotlib
matplotlib.use('Agg')
from decimal import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from math import sqrt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

SPINE_COLOUR = 'gray'

# Delays: list of delays in picoseconds
def plot_delays(all_delays, label, title, savefile, dir):
    bins = 200
    delays = [x for (x,y,z) in all_delays if (dir == z)]
    start = [y for (x,y,z) in all_delays if (dir == z)]
    if len(delays) == 0:
        return
    #delays.sort()
    #delays = delays[:500000]
    min_lim = min(delays)
    max_lim = max(delays)
    #diff = (min_lim + max_lim) / 10000.0
    #print(str(min_lim) + " " + str(max_lim) + " " + str(diff))
    y_min = min(all_delays)[0]-100000
    y_max = max(all_delays)[0]+100000
    x_min = min(all_delays, key = lambda t: t[1])[1]-1
    x_max = max(all_delays, key = lambda t: t[1])[1]+1

    plt.figure(str(dir)+"cdf")
    plt.hist(delays, bins=bins, density=True, cumulative=True, histtype='step', label=label)
    plt.title(title)
    plt.xlabel("Delays")
    plt.ylabel("CDF")
    # Set legend below the graph
    ax = plt.gca()
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='small')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000) + " ns"))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
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
    filename = savefile + "_delays_cdf.svg"
    plt.savefig(filename)

    plt.figure(str(dir)+"log_cdf")
    plt.hist(delays, bins=np.logspace(np.log10(min_lim), np.log10(max_lim), 200), density=True, cumulative=True, histtype='step', label=label)
    plt.title(title)
    plt.xlabel("Delays")
    plt.ylabel("CDF")
    # Set legend below the graph
    plt.gca().set_xscale("log")
    ax = plt.gca()
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000) + " ns"))
    #ax.get_xaxis().set_minor_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000)))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
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
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays_log_cdf.svg"
    plt.savefig(filename)


    plt.figure(str(dir)+"bar")
    plt.hist(delays, bins=bins, label=label)
    plt.axvline(np.mean(delays), color='k', linestyle='dashed', linewidth=1)
    std = np.std(delays)
    plt.title(title)
    plt.xlabel("Delays")
    plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    at = matplotlib.offsetbox.AnchoredText('Std: ' + "{:.3f}".format(std/1000) + " ns", loc='upper right', prop=dict(size=8))
    ax.add_artist(at)
    plt.setp(ax.get_xticklabels(), rotation=15, horizontalalignment='right', fontsize='small')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000) + " ns"))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays.svg"
    plt.savefig(filename)


    plt.figure(str(dir)+"log_bar")
    plt.hist(delays, bins=np.logspace(np.log10(min_lim), np.log10(max_lim), 100), label=label)
    plt.axvline(np.mean(delays), color='k', linestyle='dashed', linewidth=1)
    std = np.std(delays)
    plt.title(title)
    plt.xlabel("Delays")
    plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    ax.set_xscale("log")
    at = matplotlib.offsetbox.AnchoredText('Std: ' + "{:.3f}".format(std/1000) + " ns",
                      loc='upper right', prop=dict(size=8))
    ax.add_artist(at)
    plt.setp(ax.get_xticklabels(), rotation=15, horizontalalignment='right', fontsize='x-small')
    #ax.get_xaxis().set_major_locator(matplotlib.ticker.LinearLocator())
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000) + " ns"))
    #ax.get_xaxis().set_minor_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000)))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays_log.svg"
    plt.savefig(filename)


    plt.figure(str(dir) + "heat")
    plt.title(title)
    plt.xlabel("Start time (s)")
    plt.ylabel("Delays")
    cmap = plt.cm.plasma
    ##cmap = plt.cm.RdYlGn
    plt.ylim(y_min, y_max)
    plt.hist2d(start, delays, bins=200, cmap=cmap, norm=matplotlib.colors.LogNorm(vmin=2), range=[[x_min, x_max], [y_min, y_max]])
    cb = plt.colorbar()
    cb.set_label('Number of packets')
    # Set legend below the graph
    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000) + " ns"))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays_by_departure_time.svg"
    plt.savefig(filename)


# File format is as follows:
# A line consists of:
# delay ns, delay ps, n.o. matches, _, capture time (s.ps), capture time (s.ns), length, data, -->, _, time (s.ps), time (s.ns), length
def extract_delays(file, limit):
    delays = []
    bad = 0
    very_bad = 0
    skipped = 0
    for line in file:
        items = line.split(",")
        if items[2] != "1":
            skipped = skipped + 1
            continue
        if (abs(int(items[0])) > 10000000):
            very_bad = very_bad + 1
            print(line)
            continue
        if limit != -1 and (abs(int(items[1])) > limit):
            bad = bad + 1
            continue
        if (int(items[1]) > 0):
            delays.append((int(items[1]), float(items[4]), 1))
        else:
            delays.append((abs(int(items[1])), float(items[8 + (int(items[2])-1)*4+2]), -1))
    print("above limit packet matches: " + str(bad) + " limit: " + str(limit) + "ps")
    print("very bad packet matches: " + str(very_bad))
    print("skipped because more than 1 match: " + str(skipped))
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
