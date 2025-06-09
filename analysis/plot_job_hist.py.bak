'''

Copyright (C) 2023 University of Central Florida

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

Created by Alexander Goponenko at 9/26/23

'''
import os
import glob
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# names of columns in swf files
col_names = [
    'job_id',
    'Submit Time',
    'Wait Time',
    'Run Time',
    'Number of Allocated Processors',
    'Average CPU Time Used',
    'Used Memory',
    'Requested Number of Processors',
    'Requested Time',
    'Requested Memory',
    'Status',
    'User ID',
    'Group ID',
    'Executable',
    'Queue Number',
    'Partition Number',
    'Preceding Job Number',  # also is reused to store number of "underpredictions"
    'Think Time'  # also is reused to store predictions
]


def plot_dist(x_name, y_name, df, ax, title, scale='log'):
  # maxv = max(df[y].max(), df[x].max())
  # minv = min(df[y].min(), df[x].min())
  # delta = maxv - minv
  # margin = delta * .1
  # maxv += margin
  # minv -= margin
  # lim = (minv, maxv)
  # # mybins = np.logspace(np.log10(minv), np.log10(maxv), 50)

  # extent = (minv, maxv, minv, maxv)
  # print(extent)
  xlim = None
  ylim = None
  print(ax)
  x = df[x_name]
  y = df[y_name]
  xlim = (x.min(), x.max())
  ylim = (y.min(), y.max())
  if scale == 'log':
    x_space = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]), 50)
    y_space = np.logspace(np.log10(ylim[0]), np.log10(ylim[1]), 50)
    x_scale = 'log'
    y_scale = 'log'
  else:
    x_space = np.linspace(xlim[0], xlim[1], 50)
    y_space = np.linspace(ylim[0], ylim[1], 50)
     
  # plot 2D hitmap
  # ax.hist2d(df[x], df[y], bins=50)
  ax.hist2d(x, y, bins=(x_space, y_space), cmap='Blues')
  ax.set_xscale(x_scale)
  ax.set_yscale(y_scale)
  ax.set_xlabel(x_name)
  ax.set_ylabel(y_name)





def plot_job_hist(filename, ax):
  # read swf file
  df = pd.read_csv(filename, sep='\s+', header=None, names=col_names, comment=';')
  print(df.head())
  plot_dist('Run Time', 'Requested Number of Processors', df, ax, os.path.basename(filename))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot histogram of jobs' runtime and size for all swf files in input directory")
    parser.add_argument('input_file', help="filename")
    args = parser.parse_args()
    input_file = args.input_file
    print (input_file)
    # create figure
    fig, ax = plt.subplots(1, 1, figsize=(4, 4))
    fig.subplots_adjust(bottom=0.15, left=0.15)
    plot_job_hist(input_file, ax)

    plt.show()

        
        

