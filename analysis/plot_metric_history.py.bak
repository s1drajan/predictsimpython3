'''
This script crawls all the pathnames matching the specified pattern
and plots the history of the values of the specified metric over time.
A separate figure is created for each dataset that is extracted from the pathnames.

Created by Alexander Goponenko

Usage:
    python2 plot_metric_history.py <glob_path_pattern> <metric_name>

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
import glob
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    'Preceding Job Number',
    'Think Time'
]

def _cum_div(df, divident, divisor):
    wcs = np.cumsum(divisor)
    vcs = np.cumsum(divident)
    y = np.zeros_like(wcs)
    good_index = wcs > 0
    y[good_index] = vcs[good_index] / wcs[good_index]
    x = df['End Time']
    return x, y


def _cum_average(df, values, weights):
    return _cum_div(df, values * weights, weights)


#
# def avebsld(df):
#     bsld = np.maximum(
#         1, (df['Wait Time'] + df['Run Time']) / np.maximum(10, df['Run Time']))
#     # print(np.maximum(df['Run Time'], 10).head())
#     avebsld = np.average(bsld)
#     # print ("AVEbsld: {}".format(avebsld))
#     return avebsld
#
#
# def AF(df):
#     af = np.average(df['Flow'])
#     return af
#
#
# def AWAF(df):
#     # waf = np.sum(df['Flow'].astype(np.float64) * df['Area'].astype(np.float64)) / np.sum(df['Area'].astype(np.float64))
#     waf = np.average(df['Flow'], weights=df['Area'])
#     return waf
#

def AWpWAF(df, p):
    weights = df['Area'].astype(np.float64) * \
        df['Wait Time'].astype(np.float64)**p
    return _cum_average(df, df['Flow'], weights)


def AWpWAW(df, p):
    weights = df['Area'].astype(np.float64) * \
        df['Wait Time'].astype(np.float64)**p
    return _cum_average(df, df['Wait Time'], weights)


def ASpWAS(df, p):
    def M(p):
        M_job = n * (F ** (p + 1) - Tw ** (p + 1))
        # M_sum = M_job.sum()
        return M_job/(p+1)
    F = df['Flow'].astype(np.float64)
    Tw = df['Wait Time'].astype(np.float64)
    # Tr = df['Run Time'].astype(np.float64)
    n = df['Requested Number of Processors']
    return _cum_div(df, M(p+1), M(p))


def ASpWAF(df, p):
    """
    reduces to AWF for p=0
    """
    F = df['Flow'].astype(np.float64)
    Tw = df['Wait Time'].astype(np.float64)
    # Tr = df['Run Time'].astype(np.float64)
    n = df['Requested Number of Processors']
    weights = n * (F ** (p + 1) - Tw ** (p + 1))
    return _cum_average(df, F, weights)



def ASpWAW(df, p):
    """
    """
    F = df['Flow'].astype(np.float64)
    Tw = df['Wait Time'].astype(np.float64)
    # Tr = df['Run Time'].astype(np.float64)
    n = df['Requested Number of Processors']
    weights = n * (F ** (p + 1) - Tw ** (p + 1))
    return _cum_average(df, Tw, weights)

#
# def LpAWAF(df, p):
#     return (np.average(df['Flow'].astype(np.float64)**p, weights=df['Area'])) ** (1/p)
#
#
# def LpAWAW(df, p):
#     return (np.average(df['Wait Time'].astype(np.float64)**p, weights=df['Area'])) ** (1/p)
#
#
# def LpAWAS(df, p):
#     F = df['Flow'].astype(np.float64)
#     Tw = df['Wait Time'].astype(np.float64)
#     n = df['Requested Number of Processors']
#     M = n * (F ** (p + 1) - Tw ** (p + 1))
#     return (M.sum() / df["Area"].sum()) ** (1/p)
#
#
# def SpLpSld(df, p):
#     """
#     Specific slowdown
#     """
#     def SpecSld(df, p):
#         F = df['Flow'].astype(np.float64)
#         Tw = df['Wait Time'].astype(np.float64)
#         Tr = df['Run Time'].astype(np.float64)
#         # M_job = df['Requested Number of Processors'] * (F**(p+1) - Tw**(p+1)) / (p + 1)
#         M_job = df['Requested Number of Processors'] * (F ** (p + 1) - Tw ** (p + 1))
#         M_sum = M_job.sum()
#         # I_job = df['Requested Number of Processors'] * Tr**(p+1) / (p + 1)
#         I_job = df['Requested Number of Processors'] * Tr ** (p + 1)
#         I_sum = I_job.sum()
#         return M_sum / I_sum
#     # assert p>=1
#     return SpecSld(df,p)**(1/p)
#
#
# def AWLpSld(df, p):
#     def AWpWSld(df, p):
#         F = df['Flow'].astype(np.float64)
#         Tw = df['Wait Time'].astype(np.float64)
#         Tr = df['Run Time'].astype(np.float64)
#         M_job = df['Area'] * Tw ** p * F
#         M_sum = M_job.sum()
#         I_job = df['Area'] * Tw ** p * Tr
#         I_sum = I_job.sum()
#         return M_sum / I_sum
#     assert p >= 1
#     return AWpWSld(df, p)**(1/p)
#
#
# def AvgQueue2(df, start, end, maxNodes):
#     """
#     Calculates the average queue in seconds,
#     that is how many seconds is needed to calculate the queue
#     given full occupancy of nodes
#     """
#     # Clip off either end.
#     # This way, we don't consider jobs that started or ended outside of our interval.
#
#     # Don't consider jobs outside of our evaluated time range.
#
#     queueTimes = np.maximum(df['Submit Time'], start)
#     dequeueTimes = np.minimum(df['Start Time'], end)
#     inQueueDurations = np.maximum(dequeueTimes - queueTimes, 0)
#
#     AvgQueueInNodes = np.sum((inQueueDurations * df['Requested Number of Processors']).astype(np.float64)) / (end - start)
#     AvgQueueInClusters = AvgQueueInNodes / maxNodes
#     # AvgQueueInJobs = np.sum(inQueueDurations.astype(np.float64)) / (end - start)
#
#     return AvgQueueInClusters


metrics = [
    # ("AVEbsld", avebsld),
    # ("AF", AF),
    # ("AWAF", AWAF),
    ("AW0WAF", lambda df: AWpWAF(df, 0)),
    ("AW1WAF", lambda df: AWpWAF(df, 1)),
    ("AW2WAF", lambda df: AWpWAF(df, 2)),
    ("AW4WAF", lambda df: AWpWAF(df, 4)),
    ("AW8WAF", lambda df: AWpWAF(df, 8)),
    # ("AW1Sld", lambda df: AWLpSld(df, 1)),
    # ("AW2Sld", lambda df: AWLpSld(df, 2)),
    # ("AW4Sld", lambda df: AWLpSld(df, 4)),
    # ("AW8Sld", lambda df: AWLpSld(df, 8)),
    # ("Sp1Sld", lambda df: SpLpSld(df, 1)),
    # ("Sp2Sld", lambda df: SpLpSld(df, 2)),
    # ("Sp4Sld", lambda df: SpLpSld(df, 4)),
    # ("Sp8Sld", lambda df: SpLpSld(df, 8)),
    ("AS0WAF", lambda df: ASpWAF(df, 0)),
    ("AS1WAF", lambda df: ASpWAF(df, 1)),
    ("AS2WAF", lambda df: ASpWAF(df, 2)),
    ("AS4WAF", lambda df: ASpWAF(df, 4)),
    ("AS8WAF", lambda df: ASpWAF(df, 8)),
    ("AS0WAW", lambda df: ASpWAW(df, 0)),
    ("AS1WAW", lambda df: ASpWAW(df, 1)),
    ("AS2WAW", lambda df: ASpWAW(df, 2)),
    ("AS4WAW", lambda df: ASpWAW(df, 4)),
    ("AS8WAW", lambda df: ASpWAW(df, 8)),
    ("AS0WAS", lambda df: ASpWAS(df, 0)),
    ("AS1WAS", lambda df: ASpWAS(df, 1)),
    ("AS2WAS", lambda df: ASpWAS(df, 2)),
    ("AS4WAS", lambda df: ASpWAS(df, 4)),
    ("AS8WAS", lambda df: ASpWAS(df, 8)),
# ] + [("L{}AWAS".format(i), lambda df, i=i: LpAWAS(df, i)) for i in [1, 2, 3, 5, 9]
] + [("AW{}WAW".format(i), lambda df, i=i: AWpWAW(df, i)) for i in [0, 1, 2, 4, 8]
]

def get_header():
    # return ["Queue"] + [x[0] for x in metrics]
    return [x[0] for x in metrics]


def calculate_metric_history(in_file, metric_funciton):
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
    # print ("Earliest time: {}".format(earliest_good_time))

    # # uncomment in case we want to include all data
    # latest_good_time = df['End Time'].max()
    # earliest_good_time = df['Submit Time'].min()

    df = df[earliest_good_time < df['End Time']]
    df = df[df['End Time'] < latest_good_time]

    res = metric_funciton(df)

    return res


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print ("Usage: {} <input_folder> <metric>".format(os.path.basename(__file__)))
    input_dir = sys.argv[1]
    metric_name = sys.argv[2]
    m_dic = {x[0]: x[1] for x in metrics}
    metric_f = m_dic[metric_name]
    # input_files = glob.glob(os.path.join(input_dir, "*"))
    input_files = glob.glob(input_dir)
    input_files.sort()
    print (input_files)
    fig_dic = {}
    for file in input_files:
        print("analyzing {}".format(os.path.basename(file)))
        data, config = os.path.basename(file).split('___')
        if data in fig_dic:
            fig, ax = fig_dic[data]
        else:
            new_fig = plt.subplots()
            fig_dic[data] = new_fig
            fig, ax = new_fig
        config = config.split('.')[0]
        res = calculate_metric_history(file, metric_f)
        ax.plot(res[0], res[1], label=config)

    for data in fig_dic.keys():
        fig, ax = fig_dic[data]
        ax.set_title("{} for {}".format(metric_name, data))
        ax.legend()

    plt.show()
