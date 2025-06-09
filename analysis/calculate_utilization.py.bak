'''
This script calculate the average utilization of nodes.
This script is based on calculate_metrics.

Created by Alexander Goponenko

Usage:
    calculate_utilization.py <swf_file>

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
from docopt import docopt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math

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


def Utilization(df, start, end, maxNodes):
  """

    :param df: unfiltered input dataframe (which include 'Submit Time', 'Start Time', and 'Area')
    :param start: start time of the evaluated interval
    :param end: end time of the evaluated interval
    :param maxNodes: the number of nodes in the cluster
    """

  # Clip off either end.
  # This way, we don't consider jobs' wait time outside of our interval.
  startTimes = np.maximum(df['Start Time'], start)
  endTimes = np.minimum(df['End Time'], end)

  durations = np.maximum(endTimes - startTimes, 0)


  utilization = np.sum((durations * df['Requested Number of Processors']).astype(np.float64)) / (maxNodes *(end - start))

  return utilization



def calculate_different_utilizations(in_file):
  # extracting number of processors
  numNodes = None
  input_file = open(in_file)
  for line in input_file:
    if (line.lstrip().startswith(';')):
      if (line.lstrip().startswith('; MaxProcs:')):
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

  # "..to reduce warmup and cooldown effects, the first 1 percent of terminated jobs
  # and those terminating after the last arrival were not included .."
  # https://doi.org/10.1109/TPDS.2007.70606
  latest_good_time = df['Submit Time'].max()
  # print ("Latest time: {}".format(latest_good_time))
  end_times = sorted(df['End Time'])
  earliest_good_time = end_times[len(end_times)//100]
  print("Utilization excluding 1% of first jobs and cooldown: {}".format(Utilization(df, earliest_good_time, latest_good_time, numNodes)))


  print("Whole interval Utilization: {}".format(Utilization(df, df['Submit Time'].min(), df['End Time'].max(), numNodes)))

  print("Utilization excluding cooldown: {}".format(Utilization(df, df['Submit Time'].min(), latest_good_time, numNodes)))

  print("Utilization excluding warm-up: {}".format(Utilization(df, earliest_good_time, df['End Time'].max(), numNodes)))



if __name__ == "__main__":
  # Retrieve arguments
  # arguments = docopt(__doc__, version='1.0.0rc2')
  arguments, exception = docopt(__doc__, version='1.0.0rc2')

  # print(arguments)

  in_file = arguments['<swf_file>']

  calculate_different_utilizations(in_file)
