'''
This script can be run by itself, or its function calculate_metrics can
be imported into another script (for instance, it is used in analyze_folder.py)

Created by Alexander Goponenko

Usage:
    calculate_metrics.py <swf_file> [-h | --help | -p | --plot_dist | --notrim]

 Options:
    -p, --plot_dist     Create prediction vs real time distribution figure [default: False]
    --notrim            Don't trim data from left and right (all times are good) [default: False]
    -h, --help          Show this screen and exit.

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



def _average(values, weights):
  try:
    return np.average(values, weights=weights)
  except ZeroDivisionError:
    return 0


def avebsld(df):
  bsld = np.maximum(
      1,
      (df['Wait Time'] + df['Run Time']) / np.maximum(10, df['Run Time']))
  avebsld = np.average(bsld)
  return avebsld


def AF(df):
  af = np.average(df['Flow'])
  return af


def AWAF(df):
  # waf = np.sum(df['Flow'].astype(np.float64) * df['Area'].astype(np.float64)) / np.sum(df['Area'].astype(np.float64))
  waf = np.average(df['Flow'], weights=df['Area'])
  return waf


def AWWaitTime(df):
  # waf = np.sum(df['Flow'].astype(np.float64) * df['Area'].astype(np.float64)) / np.sum(df['Area'].astype(np.float64))
  waf = np.average(df['Wait Time'], weights=df['Area'])
  return waf


def AWpWAF(df, p):
  weights = df['Area'].astype(np.float64) * \
      df['Wait Time'].astype(np.float64)**p
  return _average(df['Flow'], weights=weights)


def ASpWAS(df, p):
  def M(p):
    M_job = n * (F ** (p + 1) - Tw ** (p + 1))
    M_sum = M_job.sum()
    return M_sum / (p+1)
  F = df['Flow'].astype(np.float64)
  Tw = df['Wait Time'].astype(np.float64)
  # Tr = df['Run Time'].astype(np.float64)
  n = df['Requested Number of Processors']
  return M(p+1)/M(p)


def ASpWAF(df, p):
  """
    reduces to AWF for p=0
    """
  F = df['Flow'].astype(np.float64)
  Tw = df['Wait Time'].astype(np.float64)
  # Tr = df['Run Time'].astype(np.float64)
  n = df['Requested Number of Processors']
  weights = n * (F ** (p + 1) - Tw ** (p + 1))
  return _average(F, weights=weights)


def ASpWAW(df, p):
  """
    """
  F = df['Flow'].astype(np.float64)
  Tw = df['Wait Time'].astype(np.float64)
  # Tr = df['Run Time'].astype(np.float64)
  n = df['Requested Number of Processors']
  weights = n * (F ** (p + 1) - Tw ** (p + 1))
  return _average(Tw, weights=weights)


def LpAWAF(df, p):
  return (np.average(df['Flow'].astype(np.float64)**p, weights=df['Area'])) ** (1/p)


def LpAWAW(df, p):
  return (np.average(df['Wait Time'].astype(np.float64)**p, weights=df['Area'])) ** (1/p)


def LpAWAS(df, p):
  F = df['Flow'].astype(np.float64)
  Tw = df['Wait Time'].astype(np.float64)
  n = df['Requested Number of Processors']
  M = n * (F ** (p + 1) - Tw ** (p + 1))
  return (M.sum() / df["Area"].sum()) ** (1/p)


def SpLpSld(df, p):
  """
    Specific slowdown - not yet developed

    """
  # TODO: justify&develop or delete
  def SpecSld(df, p):
    F = df['Flow'].astype(np.float64)
    Tw = df['Wait Time'].astype(np.float64)
    Tr = df['Run Time'].astype(np.float64)
    # M_job = df['Requested Number of Processors'] * (F**(p+1) - Tw**(p+1)) / (p + 1)
    M_job = df['Requested Number of Processors'] * (F ** (p + 1) - Tw ** (p + 1))
    M_sum = M_job.sum()
    # I_job = df['Requested Number of Processors'] * Tr**(p+1) / (p + 1)
    I_job = df['Requested Number of Processors'] * Tr ** (p + 1)
    I_sum = I_job.sum()
    return M_sum / I_sum
  # assert p>=1
  # FIXME: is it 1/p or 1/(p+1) ?
  return SpecSld(df,p)**(1/p)


def AWLpSld(df, p):
  """
    Lp-norm type weighted slowdown - not yet developed

    """
  # TODO: justify&develop or delete
  def AWpWSld(df, p):
    F = df['Flow'].astype(np.float64)
    Tw = df['Wait Time'].astype(np.float64)
    Tr = df['Run Time'].astype(np.float64)
    M_job = df['Area'] * Tw ** p * F
    M_sum = M_job.sum()
    I_job = df['Area'] * Tw ** p * Tr
    I_sum = I_job.sum()
    return M_sum / I_sum
  assert p >= 1
  return AWpWSld(df, p)**(1/p)


def AvgQueue(df, start, end):
  # Clip off either end.
  # This way, we don't consider jobs that started or ended outside of our interval.

  # TODO: Confirm filtering behavior is correct. We need the non-filtered df.

  # Start at the earliest submit time.
  startTime = start  # np.amin(df['Submit Time'])
  # End at the latest end time.
  endTime = end  # np.amax(df['Submit Time']+df['Wait Time']+df['Run Time'])
  adjustedJobs = df.copy()
  # Don't consider jobs outside of our evaluated time range.
  adjustedJobs = adjustedJobs[(df['Submit Time'] >= startTime) & (
      df['Submit Time']+df['Wait Time']+df['Run Time'] <= endTime)]
  # Adjust our jobs, cutting off anything outside of our interval.
  # This will eliminate the effects of warmup and cooldown.
  for idx in adjustedJobs.index:
    # Have to clip off the beginning.
    if adjustedJobs.loc[idx, 'Submit Time'] < startTime:
      if adjustedJobs.loc[idx, 'Submit Time']+adjustedJobs.loc[idx, 'Wait Time'] >= startTime:
        adjustedJobs.loc[idx, 'Wait Time'] -= startTime - \
            adjustedJobs.loc[idx, 'Submit Time']
      elif adjustedJobs.loc[idx, 'Submit Time']+adjustedJobs.loc[idx, 'Wait Time']+adjustedJobs.loc[idx, 'Run Time'] > startTime:
        adjustedJobs.loc[idx, 'Wait Time'] = 0
        adjustedJobs.loc[idx, 'Run Time'] -= startTime - (
            adjustedJobs.loc[idx, 'Submit Time']+adjustedJobs.loc[idx, 'Wait Time'])
      adjustedJobs.loc[idx, 'Submit Time'] = startTime
    # Have to clip off the end.
    if adjustedJobs.loc[idx, 'Submit Time']+adjustedJobs.loc[idx, 'Wait Time']+adjustedJobs.loc[idx, 'Run Time'] > endTime:
      if adjustedJobs.loc[idx, 'Submit Time']+adjustedJobs.loc[idx, 'Wait Time'] <= endTime:
        adjustedJobs.loc[idx, 'Wait Time'] -= (
            adjustedJobs.loc[idx, 'Submit Time']+adjustedJobs.loc[idx, 'Wait Time']) - endTime
        adjustedJobs.loc[idx, 'Run Time'] = 0
      elif adjustedJobs.loc[idx, 'Submit Time'] < endTime:
        adjustedJobs.loc[idx, 'Run Time'] -= (adjustedJobs.loc[idx, 'Submit Time'] +
                                              adjustedJobs.loc[idx, 'Wait Time']+adjustedJobs.loc[idx, 'Run Time']) - endTime
  # Unweighted.
  # return np.sum(adjustedJobs['Wait Time'])/(endTime-startTime)

  # Weighted.
  return (np.sum(np.multiply(adjustedJobs['Wait Time'], adjustedJobs['Area']))/(endTime-startTime))/np.average(adjustedJobs['Area'])

def R2(df, pred, real):
  pred = df[pred]
  real = df[real]
  y_bar = np.sum(real)/len(real)
  # Get absolute differences.
  SS_res = np.sum(np.square(np.subtract(pred, real)))
  SS_tot = np.sum(np.square(np.subtract(y_bar, real)))
  r_squared = 1-SS_res/SS_tot
  return r_squared

def check_resources(df, maxNodes):
  # This is a sanity check to make sure that the number of requested processors
  # is always less than or equal to the number of allocated processors.
  df1 = df[['Start Time']].copy()
  df1['delta'] = df['Requested Number of Processors']
  # sort by time
  df1 = df1.sort_values(by=['Start Time'])
  # remove duplicated times summing the delta
  df1 = df1.groupby('Start Time').sum()
  # set index to time and remove all but 'in' column
  # df1 = df1.set_index('Start Time')['delta']
  df2 = df[['End Time']].copy()
  df2['delta'] = -df['Requested Number of Processors']
  df2 = df2.sort_values(by=['End Time'])
  df2 = df2.groupby('End Time').sum()
  # df2 = df2.set_index('End Time')['delta']
  # combine the two dataframes
  df3 = pd.concat([df1, df2])
  # fill in missing values with zero
  df3 = df3.fillna(0)
  # sort by time
  df3 = df3.sort_index()
  # sum the sum column cumulatively
  df3['sum'] = df3['delta'].cumsum()
  # remove duplicated times
  df3 = df3[~df3.index.duplicated(keep='last')]
  # print(df3)
  # check that the sum is always less than or equal to the number of nodes
  if (df3['sum'] > maxNodes).any():
    # return rows where the sum is greater than the number of nodes and the next with a different value
    failed_rows = df3['sum'] > maxNodes
    return df3[(failed_rows) | (failed_rows.shift(1))]
  else:
    return None



def plot_dist(df, fig_filename=None):
  pred = 'Think Time'
  real = 'Run Time'

  maxv = max(df[pred].max(), df[real].max())
  minv = min(df[pred].min(), df[real].min())

  linthresh = 10 # 10 for rate, 100 for total

  for i in [real, pred]:
    indexes = df[i] < linthresh
    df[i][indexes] = linthresh * 10 ** (df[i][indexes] / linthresh - 1)

  maxv = max(df[pred].max(), df[real].max()) * 2
  minv = min(df[pred].min(), df[real].min()) / 2
  lim = (minv, maxv)
  mybins = np.logspace(np.log10(minv), np.log10(maxv), 40)

  extent = (np.log10(minv), np.log10(maxv), np.log10(minv), np.log10(maxv),)
  #print('Extent: ', extent)

  g = sns.JointGrid(real, pred, df, xlim=lim, ylim=lim)
  g.fig.subplots_adjust(left=0.1, top=0.95)
  g.plot_marginals(sns.distplot, hist=True, kde=False, bins=mybins)
  # g.plot_joint(plt.scatter, edgecolor='white')
  g.plot_joint(plt.hexbin, bins='log', xscale='log', yscale='log', cmap=plt.cm.Blues, extent=extent, gridsize=40)

  g.ax_joint.set_xscale('log')
  g.ax_joint.set_yscale('log')
  g.ax_marg_x.set_xscale('log')
  g.ax_marg_y.set_yscale('log')
  #g.fig.suptitle(filename)
  plt.draw()

  cbar_ax = g.fig.add_axes([.91, 0.12, .02, .6])
  g.fig.subplots_adjust(right=0.9, top=0.9)
  cb = plt.colorbar(cax=cbar_ax)

  #print("tst ", g.ax_joint.get_xticklabels())
  labels = [w.get_text() for w in g.ax_joint.get_xticklabels()]
  #print('old labels: ', labels)
  locs = list(g.ax_joint.get_xticks())
  new_locs = [linthresh/10]
  new_labels = ['$\\mathdefault{0}$']
  for i in range(len(locs)):
    if maxv >= locs[i] >= linthresh:
      new_locs.append(locs[i])
      new_label = '$\\mathdefault{10^{%d}}$' % round(math.log10(locs[i]))
      new_labels.append(new_label)
  #print(new_locs, new_labels)
  g.ax_joint.set_xticklabels(new_labels)
  g.ax_joint.set_xticks(new_locs)
  g.ax_joint.set_yticklabels(new_labels)
  g.ax_joint.set_yticks(new_locs)
  g.ax_joint.axvline(linthresh, linestyle=':', color='#ff9999')
  g.ax_joint.axhline(linthresh, linestyle=':', color='#ff9999')

  # Compute errors.
  error = np.subtract(df[pred], df[real])
  # Average error is the average distance from the line. Must always be positive.
  avg = np.sum(np.abs(error))/len(error)

  # Compute r squared.
  r_squared = R2(df, pred, real)

  g.fig.suptitle(fig_filename+'\n'+'Avg error: '+str(avg)+'\nabs r2: '+str(r_squared))

  if fig_filename:
    plt.savefig(fig_filename+".png")
  else:
    plt.draw()
    plt.show()
  plt.close()


def Utilization(df, start, end, maxNodes):
  """
    Calculates the average utilization of the cluster over the interval
    
    :param df: unfiltered input dataframe (which include 'Submit Time', 'Start Time', and 'Number of Allocated Processors')
    :param start: start time of the evaluated interval
    :param end: end time of the evaluated interval
    :param maxNodes: the number of nodes in the cluster
    """

  # Clip off start and end times.
  startTimes = np.maximum(df['Start Time'], start)
  endTimes = np.minimum(df['End Time'], end)
  remaingJobs = startTimes < endTimes

  # Calculate the total utilization area
  totalArea = np.sum((endTimes[remaingJobs] - startTimes[remaingJobs]) * df['Number of Allocated Processors'][remaingJobs])

  # Calculate the available area
  availableArea = (end - start) * maxNodes

  return totalArea / availableArea


def AvgQueueCT(df, start, end, maxNodes):
  """
    Calculates the average queue in cluster time (seconds),
    that is how many seconds (on average) is needed
    to calculate the queue given full occupancy of nodes

    :param df: unfiltered input dataframe (which include 'Submit Time', 'Start Time', and 'Area')
    :param start: start time of the evaluated interval
    :param end: end time of the evaluated interval
    :param maxNodes: the number of nodes in the cluster
    """

  # Clip off either end.
  # This way, we don't consider jobs' wait time outside of our interval.
  queueTimes = np.maximum(df['Submit Time'], start)
  dequeueTimes = np.minimum(df['Start Time'], end)
  # Calculate in-queue durations (wait time inside the interval) of jobs
  # fixing jobs with wait time fully outside of our evaluated time range
  # (they will have negative in-queue duration)
  inQueueDurations = np.maximum(dequeueTimes - queueTimes, 0)

  # AvgQueueInJobs = np.sum(inQueueDurations.astype(np.float64)) / (end - start)
  # AvgQueueInNodes = np.sum((inQueueDurations * df['Requested Number of Processors']).astype(np.float64)) / (end - start)
  # AvgQueueInClusters = AvgQueueInNodes / maxNodes
  AvgQueuedArea = np.sum((inQueueDurations * df['Area']).astype(np.float64)) / (end - start)
  AvgQueuedClusterTime = AvgQueuedArea / maxNodes

  return AvgQueuedClusterTime



metrics = [
    ("AVEbsld", avebsld),
    ("AF", AF),
    ("AWAF", AWAF),
    # ("AW1WAF", lambda df: AWpWAF(df, 1)),
    # ("AW2WAF", lambda df: AWpWAF(df, 2)),
    # ("AW4WAF", lambda df: AWpWAF(df, 4)),
    # ("AW8WAF", lambda df: AWpWAF(df, 8)),
    # ("AS0WAF", lambda df: ASpWAF(df, 0)),
    ("AS1WAF", lambda df: ASpWAF(df, 1)),
    ("AS2WAF", lambda df: ASpWAF(df, 2)),
    # ("AS4WAF", lambda df: ASpWAF(df, 4)),
    # ("AS8WAF", lambda df: ASpWAF(df, 8)),
    # ("AS0WAW", lambda df: ASpWAW(df, 0)),
    # ("AS1WAW", lambda df: ASpWAW(df, 1)),
    # ("AS2WAW", lambda df: ASpWAW(df, 2)),
    # ("AS4WAW", lambda df: ASpWAW(df, 4)),
    # ("AS8WAW", lambda df: ASpWAW(df, 8)),
    ("AS0WAS", lambda df: ASpWAS(df, 0)),
    ("AS1WAS", lambda df: ASpWAS(df, 1)),
    ("AS2WAS", lambda df: ASpWAS(df, 2)),
    # ("AS4WAS", lambda df: ASpWAS(df, 4)),
    # ("AS8WAS", lambda df: ASpWAS(df, 8)),
    ("R2", lambda df: R2(df, 'Think Time', 'Run Time')),
# ] + [("L{}AWAS".format(i), lambda df, i=i: LpAWAS(df, i)) for i in [1, 2, 3, 5, 9]
]


def get_header():
  return ["QueueCT"] + [x[0] for x in metrics] + ["Utilization"]
  # return [x[0] for x in metrics]


def calculate_metrics(in_file, do_plot=False, notrim=False):
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

  check = check_resources(df, numNodes)
  if check is not None:
    print("Warning: requested number of processors is greater than the number of nodes in the cluster")
    print(check)

  print("Total # of jobs: {}".format(len(df)))
  if notrim:
    # we want to include all data
    print("Not trimming data")
    latest_good_time = df['End Time'].max()
    earliest_good_time = df['Submit Time'].min()
  else:
    # "..to reduce warmup and cooldown effects, the first 1 percent of terminated jobs
    #     # and those terminating after the last arrival were not included .."
    #     # https://doi.org/10.1109/TPDS.2007.70606
    print("Trimming data")
    latest_good_time = df['Submit Time'].max()
    # print ("Latest time: {}".format(latest_good_time))
    end_times = sorted(df['End Time'])
    earliest_good_time = end_times[len(end_times)//100]



  res = []
  # res.append(AvgQueue(df, earliest_good_time, latest_good_time))
  res.append(AvgQueueCT(df, earliest_good_time, latest_good_time, numNodes))

  # print ("Earliest time: {}".format(earliest_good_time))
  df_tr = df[earliest_good_time <= df['End Time']]
  df_tr = df[df['End Time'] <= latest_good_time]

  print("Number of jobs after trimming: {}".format(len(df_tr)))

  for x in metrics:
    res.append(x[1](df_tr))

  # compute utilization
  res.append(Utilization(df, earliest_good_time, latest_good_time, numNodes))


  bar_count = 100
  # Compute influence of R^2 classes.
  if do_plot:
    plot_dist(df_tr, in_file)

  return res


if __name__ == "__main__":
  # Retrieve arguments
  # arguments = docopt(__doc__, version='1.0.0rc2')
  arguments, exception = docopt(__doc__, version='1.0.0rc2')

  # print(arguments)

  in_file = arguments['<swf_file>']
  do_plot = arguments['--plot_dist']
  notrim = arguments['--notrim']

  values = calculate_metrics(in_file, do_plot, notrim)
  header = get_header()

  print(values)
  for key, value in zip(header, values):
    print("{}: {}".format(key, value))
