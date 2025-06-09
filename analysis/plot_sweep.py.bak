'''
"Sweep plot" for publication

Created by Alexander Goponenko

Usage:
    plot_queue_length.py <swf_file>

 Options:
    -h, --help  Show this screen and exit.

Copyright (C) 2022 University of Central Florida

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

from __future__ import division

import sys
import os
import csv

from docopt import docopt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


Metrics_2_Plot = [("AVEbsld", "$BSLD$"),
                  ("AF", "$AF$"),
                  ("AWAF", "$AWF$"),
                  ("AS2WAS", "$P^2SF$")]

Colors = ['crimson', 'green', 'deepskyblue', 'darkviolet']


def plot_sweep_from_csv(in_name):
    df = pd.read_csv(in_name)
    print(df.head())

    df = df.sort_values("config")

    dataset = df["data"][0] # the file is assumed to contain same data


    x = df["config"]/1000

    n_plots = len(Metrics_2_Plot)

    fig, axs = plt.subplots(n_plots, sharex="all", gridspec_kw={'hspace': .4}, figsize=(3.6, 4.8))

    axs[0].set_xscale('log')
    yticks = mtick.FormatStrFormatter("%1.1e")

    for data, ax, c in zip(Metrics_2_Plot, axs, Colors):
        ax.axvline(x=1.00, color="grey", lw=.75)
        ax.plot(x, df[data[0]], color=c)
        # ax.set_title(data[1], loc="right", y=1, x=.98, pad=-17, backgroundcolor=(1.0,1.0,1.0,0.95))
        # ax.yaxis.set_major_formatter(yticks)
        ax.set_ylabel(data[1], fontsize=12)
        ax.ticklabel_format(style='sci', axis='y', useOffset=False, scilimits=(-2,3), useMathText=True)

    ax=axs[len(axs)-1]
    fmt = '%0.1f'  # Format you want the ticks, e.g. '40%'
    xticks = mtick.FormatStrFormatter(fmt)
    sticks = mtick.FormatStrFormatter("")

    ax.xaxis.set_major_formatter(xticks)
    ax.set_xlim((0.50, 2.15))
    ax.set_xticks([0.50, 1.00, 2.00])
    ax.set_xlabel("$E_j/D_j$", fontsize=12)
    ax.xaxis.set_major_formatter(xticks)
    ax.xaxis.set_minor_formatter(sticks)

    # ax.ticklabel_format(style='plain', axis='x', useOffset=False)

    fig.subplots_adjust(left=0.2, top=0.95)
    fig.align_ylabels()
    plt.show()




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: python {} <csv_sweep_file>".format(os.path.basename(__file__)))
        exit(1)
    in_name = sys.argv[1]

    plot_sweep_from_csv(in_name)
