'''
This script makes Fig. 3 int SBACPAD2022 papers

Usage:
Create swf files and adjust file location in the script.
Then run the script.

Created by Alexander Goponenko

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

import os.path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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



def plot_cf(in_files, names, ylim):
  sfs = []
  for in_file in in_files:
    # extracting number of processors
    numNodes = None
    input_file = open(in_file)
    for line in input_file:
      if line.lstrip().startswith(';'):
        if line.lstrip().startswith('; MaxProcs:'):
          numNodes = int(line.strip()[11:])
          break
        else:
          continue
      else:
        break
    input_file.close()
    assert numNodes is not None

    # read date and do the rest...
    df = pd.read_csv(in_file, sep='\s+', comment=';',
                     header=None, names=col_names)
    df['Start Time'] = df['Submit Time'] + df['Wait Time']
    df['End Time'] = df['Start Time'] + df['Run Time']
    df['Flow'] = df['Wait Time'] + df['Run Time']
    df['Area'] = df['Requested Number of Processors'] * df['Run Time']
    df['Slowdown'] = df['Flow'] / df['Run Time']
    df['Lost Opportunity'] = df['Wait Time'] * df['Area']
    df['Count'] = 1

    # if notrim:
    #   # we want to include all data
    #   latest_good_time = df['End Time'].max()
    #   earliest_good_time = df['Submit Time'].min()
    # else:
    #   # "..to reduce warmup and cooldown effects, the first 1 percent of terminated jobs
    #   #     # and those terminating after the last arrival were not included .."
    #   #     # https://doi.org/10.1109/TPDS.2007.70606
    #   latest_good_time = df['Submit Time'].max()
    #   # print ("Latest time: {}".format(latest_good_time))
    #   end_times = sorted(df['End Time'])
    #   earliest_good_time = end_times[len(end_times) // 100]
    #
    # df = df[earliest_good_time < df['End Time']]
    # df = df[df['End Time'] < latest_good_time]

    sf = df.sort_values(by=['Area'])
    sf['WCum LO'] = sf['Lost Opportunity'].cumsum()
    sf['WCDF'] = sf['Area'].cumsum() / sf['Area'].sum()
    sf['CDF'] = sf['Count'].cumsum() / sf['Count'].sum()
    sfs.append(sf)

  fig, axs = plt.subplots(2,
                          sharex=True,
                          # gridspec_kw={'hspace': 0, 'height_ratios': [3, 2, 2]},
                          figsize=(6, 6))
  ax = axs[0]
  sf = sfs[0]
  ax.step(sf['Area'], sf['CDF'], where='post', linewidth=2, label="Number of jobs")
  ax.step(sf['Area'], sf['WCDF'], where='post',  linewidth=2, linestyle='dashed', label="Job areas")
  ax.set_ylim(0, 1.01)
  ax.set_ylabel("Cumulative fraction")
  ax.legend()

  ax = axs[1]
  styles = ['dotted', 'dashed', 'solid', 'dashdot']
  for sf, n, s in zip(sfs, names, styles):
    ax.step(sf['Area'], sf['WCum LO'], where='post', linewidth=2, linestyle=s, label=n)
  ax.set_ylim(0, ylim)
  maxx = sfs[0]['Area'].max()
  ax.set_xlim(-0.005*maxx, 1.002*maxx)
  ax.ticklabel_format(style='sci', scilimits=(0,0))

  ax.set_xlabel('Job area')
  ax.set_ylabel("Cumulative wait area")
  ax.legend()

  fig.align_ylabels()

  # change offset labels
  plt.tight_layout()
  plt.draw()
  fig.canvas.draw()

  offset = ax.yaxis.get_offset_text()
  position = offset.get_position()
  transf = offset.get_transform()
  position = ax.transData.inverted().transform(transf.transform(position))
  print(offset)
  print(position)
  old_text = offset.get_text()
  ax.yaxis.offsetText.set_visible(False)
  order = old_text.split('e')[-1]
  new_text = "$\\times 10^{" + str(order) + "}\\times nodes \\times s$"
  ax.text(position[0], position[1], new_text, horizontalalignment='left', verticalalignment='bottom', transform=ax.transData)

  offset = ax.xaxis.get_offset_text()
  position = offset.get_position()
  transf = offset.get_transform()
  position = ax.transData.inverted().transform(transf.transform(position))
  old_text = offset.get_text()
  ax.xaxis.offsetText.set_visible(False)
  order = old_text.split('e')[-1]
  new_text = "$\\times 10^{" + str(order) + "}\\times nodes \\times s$"
  ax.text(position[0], position[1], new_text, horizontalalignment='right', verticalalignment='top', transform=ax.transData)
  # ax.xaxis.set_offset_text(offset)
  plt.draw()
  fig.canvas.draw()
  print(old_text)

  plt.show()

  return



if __name__ == "__main__":

  prefix = '../results/algorithms'
  in_files = [os.path.join(prefix, fn) for fn in [
    'SDSC-SP2___SAF-PureBF_Clairvoyant.swf',
    'SDSC-SP2___EASY-SJBF_Clairvoyant.swf',
    'SDSC-SP2___PureBF_Clairvoyant.swf',
    'SDSC-SP2___LAF-PureBF_Clairvoyant.swf'
  ]]
  names = [
    'SAF-JustBF',
    'EASY-SJBF',
    'JustBF',
    'LAF-JustBF'
  ]
  ylim = .8e15

  plot_cf(in_files, names, ylim)
