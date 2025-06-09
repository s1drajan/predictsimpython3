'''
Plot of queue length based on swf files (Fig. 5 in DEBS2024 paper)

Created by Alexander Goponenko

Usage:
    calculate_queue_length.py <swf_file1> <swf_file2> ...

 Options:
    -h, --help  Show this screen and exit.

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
'''

import argparse
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import progressbar
from usage_tracker import UsageTracker

header = [
    'job_id', 'Submit Time', 'Wait Time', 'Run Time',
    'Number of Allocated Processors', 'Average CPU Time Used', 'Used Memory',
    'Requested Number of Processors', 'Requested Time', 'Requested Memory',
    'Status', 'User ID', 'Group ID', 'Executable', 'Queue Number',
    'Partition Number', 'Preceding Job Number', 'Think Time'
]


def write_profile_to_file(profile, timestamps, out_file):
  with open(out_file, 'w') as f:
    f.write('timestamp,problem_size\n')
    for i in range(len(timestamps)):
      f.write('{},{}\n'.format(timestamps[i], profile.value_at(timestamps[i])))


def calculate_queue_length(in_file):
  df = pd.read_csv(in_file, sep='\s+', comment=';', header=None, names=header)
  print(df.head())


  df["Start Time"] = df["Submit Time"] + df["Wait Time"]
  df["End Time"] = df["Start Time"] + df["Run Time"]

  df["Area"] = df["Run Time"] * df["Number of Allocated Processors"]
  df["Count"] = 1

  # copy "Start Time", "Area", and "Count" into a new dataframe and rename columns
  df_out = df[["Start Time", "Area", "Count"]].copy()
  df_out.rename(columns={"Start Time": "Time"}, inplace=True)
  # when job starts, area is removed from queue
  df_out["Area"] = -df_out["Area"]
  df_out["Count"] = -df_out["Count"]

  df_in = df[["Submit Time", "Area", "Count"]].copy()
  df_in.rename(columns={"Submit Time": "Time"}, inplace=True)

  # concatenate the two dataframes, sort by time, and reset index
  df_queue = pd.concat([df_out, df_in])
  # df_queue.sort_values(by=["Time"], inplace=True)
  df_queue.reset_index(drop=True, inplace=True)

  # combine rows with same time
  df_queue = df_queue.groupby("Time").sum()

  # sort and calculate cumulative sum
  df_queue.sort_values(by=["Time"], inplace=True)
  df_queue["Area"] = df_queue["Area"].cumsum()
  df_queue["Count"] = df_queue["Count"].cumsum()

  # print(df_queue)

  # write to file
  # df_queue.to_csv(in_file + '.qarea.csv', index=False)

  return df_queue


def calculate_untilization(in_file):
  df = pd.read_csv(in_file, sep='\s+', comment=';', header=None, names=header)

  df["Start Time"] = df["Submit Time"] + df["Wait Time"]
  df["End Time"] = df["Start Time"] + df["Run Time"]

  # copy "Start Time", "Processors"into a new dataframe and rename columns
  df_in = df[["Start Time", "Requested Number of Processors"]].copy()
  df_in.rename(
      columns={
          "Start Time": "Time",
          "Requested Number of Processors": "Used CPU"
      },
      inplace=True)

  df_out = df[["End Time", "Requested Number of Processors"]].copy()
  df_out.rename(
      columns={
          "End Time": "Time",
          "Requested Number of Processors": "Used CPU"
      },
      inplace=True)
  df_out["Used CPU"] = -df_out["Used CPU"]

  # concatenate the two dataframes, sort by time, and combine rows with same time
  df_util = pd.concat([df_in, df_out])
  df_util.sort_values(by=["Time"], inplace=True)
  df_util = df_util.groupby("Time").sum()

  # sort and calculate cumulative sum
  df_util.sort_values(by=["Time"], inplace=True)
  df_util["Used CPU"] = df_util["Used CPU"].cumsum()

  return df_util


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="TODO")
  parser.add_argument('input_file', nargs="+", help="filename")
  args = parser.parse_args()
  in_file = args.input_file

  matplotlib.rc('text', usetex=True)
  # matplotlib.rc(
  #     'text.latex',
  #     # preamble='\\usepackage{bm} \\usepackage{relsize}'
  #     preamble='\\usepackage[cm]{sfmath}'
  # )
  matplotlib.rc(
      'text.latex',
      # libertine and newtxmath are for ACM style
      preamble='\\usepackage{libertine} \\usepackage[libertine]{newtxmath} \\usepackage{sfmath} \\usepackage{siunitx}'
  )
  # plt.rcParams['figure.dpi'] = 300
  # plt.rcParams["axes.formatter.use_mathtext"] = True

  markers = ['s', 'D', 'o', 'v', 'x', '*']
  colors = ['r', 'b', 'g', 'm', 'c', 'k']
  alphas = [1, 0.7, 0.5, 0.3, 0.1, 0.05]
  labels = ['List-SAF', 'CP-AF', 'undefined', 'undefined', 'undefined', 'undefined']
  styles = [':', '-', '--', '-.', '-', '--']
  widths = [2, 1, 1, 1, 1, 1]

  fig, ax = plt.subplots(1, 1, figsize=(8, 4))
  # add another y axis
  # ax2 = ax.twinx()

  for i in range(len(in_file)):
    f = in_file[i]
    marker = markers[i]
    color = colors[i]
    alpha = alphas[i]
    qa = calculate_queue_length(f)
    # ax.scatter(
    #     qa.index, qa["Count"], alpha=0.1, marker=marker, facecolors='none', edgecolors=color)
    ax.plot(
        qa.index,
        qa["Count"],
        alpha=alpha,
        color=color,
        label="$\\textit{{{}}}$".format(labels[i]),
        linestyle=styles[i],
        linewidth=widths[i],
        zorder=0)
    util = calculate_untilization(f)
    # smooth out the utilization curve
    # util["Used CPU"] = util["Used CPU"].rolling(1000).mean()
    # ax2.plot(util.index, util["Used CPU"], alpha=0.2)

  ax.margins(0.01, 0.02)
  ax.set_xlabel("Time", fontsize='16')
  ax.set_ylabel("Number of jobs in wait queue", fontsize='16')
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.tick_params(axis='both', labelsize=15)
  # fmt = matplotlib.ticker.StrMethodFormatter("${x}$")
  # fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
  # ax.yaxis.set_major_formatter(fmt)
  # ax.xaxis.set_major_formatter(fmt)
  handles, labels = ax.get_legend_handles_labels()
  leg = ax.legend(handles[::-1], labels[::-1],
      loc="upper right", fontsize='16', framealpha=1, borderaxespad=0)
  leg.get_frame().set_edgecolor('black')

  plt.tight_layout()
  plt.draw()
  fig.canvas.draw()

  offset = ax.xaxis.get_offset_text()
  position = offset.get_position()
  transf = offset.get_transform()
  position = ax.transData.inverted().transform(transf.transform(position))
  old_text = offset.get_text()
  # print(old_text)
  ax.xaxis.offsetText.set_visible(False)
  order = old_text.split('e')[-1]
  new_text = old_text[:-1] + '\\SI{}{\\second}$'
  ax.text(
      position[0],
      position[1],
      new_text,
      fontsize='16',
      horizontalalignment='right',
      verticalalignment='top',
      transform=ax.transData)
  # ax.xaxis.set_offset_text(offset)
  ax.set_rasterization_zorder(1)
  plt.draw()
  fig.canvas.draw()

  # plt.show()
  plt.savefig("queue_len.pdf", dpi=300)

  # print(qa)
