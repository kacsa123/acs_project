import sys
import argparse
import glob

import vaex
import pylab as plt
import matplotlib

from decimal import *
#import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from math import sqrt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

SPINE_COLOUR = 'gray'

# Delays: list of delays in picoseconds
def plot_delays(df_all, label, title, savefile, dir, limit):
    bins = 200
    #delays = [x for (x,y,z) in all_delays if (dir == z)]
    #start = [y for (x,y,z) in all_delays if (dir == z)]
    #if len(delays) == 0:
    #    return
    
    #y_min = min(delays)-100
    #y_max = max(delays)+100
    #x_min = min(start)-1
    #x_max = max(start)+1
    df = df_all[abs(df_all.diff) * dir == df_all.diff]
    df['pos_diff'] = np.abs(df.diff * 1000000000)

    #plt.figure(str(dir)+"cdf")
    #if limit != -1:
        #df.plot1d(df.pos_diff, shape=bins, limits=[0, limit], ylabel='No. packets');
    #else:
        #df.plot1d(df.pos_diff, shape=bins, ylabel='No. packets');
    #plt.hist(delays, bins=bins, density=True, cumulative=True, histtype='step', label=label)
    #plt.title(title)
    #plt.xlabel("Delays")
    #plt.ylabel("CDF")
    # Set legend below the graph
    #ax = plt.gca()
    #plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='small')
    #ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x) + " ns"))
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    # Limit y to 1
    #(ymin, ymax) = plt.ylim()
    #if ymax > 1:
    #    plt.ylim(ymin, 1)
    #(ymin, ymax) = plt.ylim()
    #(xmin, xmax) = plt.xlim()
    #if ymin < 0:
    #    plt.ylim(0, ymax)
    #if xmin < 0:
    #    plt.xlim(0, xmax)
    #ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    #ax.set_axisbelow(True)
    #plt.grid()
    #filename = savefile + "_delays_cdf.svg"
    #fig.savefig(filename)

    #plt.figure(str(dir)+"log_cdf")
    #plt.hist(delays, bins=np.logspace(np.log10(y_min), np.log10(y_max), 200), density=True, cumulative=True, histtype='step', label=label)
    #plt.title(title)
    #plt.xlabel("Delays")
    #plt.ylabel("CDF")
    # Set legend below the graph
    #plt.gca().set_xscale("log")
    #ax = plt.gca()
    #plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    #ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x) + " ns"))
    #ax.get_xaxis().set_minor_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x/1000)))
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    # Limit y to 1
    #(ymin, ymax) = plt.ylim()
    #if ymax > 1:
    #    plt.ylim(ymin, 1)
    #(ymin, ymax) = plt.ylim()
    #(xmin, xmax) = plt.xlim()
    #if ymin < 0:
    #    plt.ylim(0, ymax)
    #if xmin < 0:
    #    plt.xlim(0, xmax)
    #ax.set_axisbelow(True)
    #plt.grid()
    #filename = savefile + "_delays_log_cdf.svg"
    #plt.savefig(filename)


    #-----------------DONE-------------------------------------------------
    plt.figure(str(dir)+"bar")
    if limit != -1:
        df.plot1d(df.pos_diff, shape=bins, limits=[0, limit], ylabel='No. packets');
    else:
        df.plot1d(df.pos_diff, shape=bins, ylabel='No. packets');
    plt.axvline(df.mean("pos_diff"), color='k', linestyle='dashed', linewidth=1)
    std = df.std("pos_diff")
    plt.title(title)
    plt.xlabel("Delays")
    #plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    at = matplotlib.offsetbox.AnchoredText('Std: ' + "{:.3f}".format(std) + " ns", loc='upper right', prop=dict(size=8))
    ax.add_artist(at)
    plt.setp(ax.get_xticklabels(), rotation=15, horizontalalignment='right', fontsize='small')
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x) + " ns"))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays.svg"
    plt.savefig(filename)
    #----------------------------------------------------------------------------------------------
    #---------------------------------DONE---------------------------------------------------------
    plt.figure(str(dir)+"log_bar")
    log_df = np.log10(df.pos_diff)
    if limit != -1:
        df.plot1d(log_df, shape=bins, limits=[0, limit], ylabel='No. packets');
    else:
        df.plot1d(log_df, shape=bins, ylabel='No. packets');
    # plt.hist(delays, bins=np.logspace(np.log10(y_min), np.log10(y_max), 100), label=label)
    plt.axvline(df.mean(log_df), color='k', linestyle='dashed', linewidth=1)
    std = df.std(log_df)
    plt.title(title)
    plt.xlabel("log(Delays)")
    plt.ylabel("No. packets")
    # Set legend below the graph
    ax = plt.gca()
    ax.set_xscale("log")
    #at = matplotlib.offsetbox.AnchoredText('Std: ' + "{:.3f}".format(std) + " ns",
    #                  loc='upper right', prop=dict(size=8))
    #ax.add_artist(at)
    plt.setp(ax.get_xticklabels(), rotation=15, horizontalalignment='right', fontsize='x-small')
    
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x) + " ns"))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays_log.svg"
    plt.savefig(filename)
    #--------------------------------------------------------------------------

    plt.figure(str(dir) + "heat")
    plt.title(title)
    plt.xlabel("Start time (s)")
    #plt.ylabel("Delays")
    cmap = plt.cm.plasma

    #plt.ylim(y_min, y_max)
    if (limit != -1):
        if (dir == -1):
            df.plot(df.start1, df.pos_diff, shape=[200,200], f="log", ylabel='Delays', colormap=cmap)
        else:
            df.plot(df.start2, df.pos_diff, shape=[200,200], f="log", ylabel='Delays', colormap=cmap)
    else:
        if (dir == -1):
            df.plot(df.start1, df.pos_diff, shape=[200,200], f="log", ylabel='Delays', colormap=cmap)
        else:
            df.plot(df.start2, df.pos_diff, shape=[200,200], f="log", ylabel='Delays', colormap=cmap)
    #plt.hist2d(start, delays, bins=200, cmap=cmap, norm=matplotlib.colors.LogNorm(vmin=2), range=[[x_min, x_max], [y_min, y_max]])
    #cb = plt.colorbar()
    #cb.set_label('Number of packets')
    # Set legend below the graph
    ax = plt.gca()
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: str(x) + " ns"))
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20), fancybox=True, shadow=True, ncol=1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)
    plt.grid()
    filename = savefile + "_delays_by_departure_time.svg"
    plt.savefig(filename)



def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', dest='dir', required=True, help="directory in which all .csv files are plotted")
    parser.add_argument('--label', dest='label', default=" ", help="label for plot")
    parser.add_argument('--title', dest='title', required=True, help="title of plot")
    parser.add_argument('--outfile', dest='savefile', required=True, help="name of output file")
    parser.add_argument('--limit', dest='limit', default="-1", help="limit in ns. Remove all packets with higher delays")
    args = parser.parse_args(args)
    
    
    #files = glob.glob(args.dir+'/*.csv')
    #for file in files:
        #convert=True
    	#df_tmp = vaex.from_csv(file, copy_index=False, names=["data", "len", "start1", "port1", "start2", "port2", "diff"])
    
    #df = vaex.open(args.dir+'/*.csv.hdf5')
    print("opening stuff")
    #df = vaex.open(args.dir+'/*.csv', convert=args.dir+'/bigdata.hdf5',  names=["data", "len", "start1", "port1", "start2", "port2", "diff"])
    df =  vaex.open(args.dir+'/bigdata.hdf5')

    #extract_delays(f, int(args.limit), client_delays, client_start, server_delays, server_start)
    print("Make plot for " + args.dir)
    plot_delays(df, args.label, args.title + " to client", args.savefile + "_to_client", -1, int(args.limit))
    print("Make second plot for " + args.dir)
    plot_delays(df, args.label, args.title + " to server", args.savefile + "_to_server", 1, int(args.limit))

if __name__ == "__main__":
    main(sys.argv[1:])
