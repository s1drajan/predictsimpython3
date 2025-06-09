'''
Rough plot of queue length based on swf file

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

from docopt import docopt
import datetime as dt
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import progressbar
from usage_tracker import UsageTracker

header = [
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


def main_proc(in_file, interval='48h'):
    df = pd.read_csv(in_file, sep='\s+', comment=';', header=None, names=header)
    print(df.head())

    bsld = np.maximum((df['Wait Time'] + df['Run Time']) / np.maximum(df['Run Time'], 10), 1)
    avebsld = np.average(bsld)
    print ("AVEbsld: {}".format(avebsld))

    # create profile
    ut_queue = UsageTracker(0)
    ut_run = UsageTracker(0)
    max_time = -1
    min_time = float('inf')
    bar = progressbar.ProgressBar(
        widgets=[
            progressbar.Percentage(),
            ' ',
            progressbar.Bar(),
            ' ' ,
            progressbar.Timer(),
            ' ',
            progressbar.ETA()
        ], 
        maxval=len(df.index)
    ).start()
    for i, row in df.iterrows():
        arr_time = row['Submit Time']
        if arr_time <= 0:
            continue
        start_time = arr_time + row['Wait Time']
        end_time = start_time + row['Run Time']
        max_time = max(max_time, end_time)
        min_time = min(min_time, arr_time)
        # ut.add_usage(start_time, end_time, row['Run Time'] * row['Number of Allocated Processors'])
        ut_queue.add_usage(arr_time, start_time, 1)
        ut_run.add_usage(start_time, end_time, 1)
        if i % 100 == 0:
          bar.update(i)
    bar.finish()
    
    d_queue = ut_queue.list # list is actually a sorted dict
    del d_queue[-1]
    d_run = ut_run.list
    del d_run[-1]

    #plot profile
    plot_util(d_queue, interval, "# waiting jobs", (1, 0, 0, .6), (1, 0, 0, 1))
    plot_util(d_run, interval, "# running jobs", (0, 0, 1, .6), ( 0, 0, 1, 1))

    plt.xlim(min_time, max_time)
    plt.title("Queue length for {}".format(os.path.basename(in_file).split('.')[0]))
    plt.legend()
    plt.show()


    return 1


def plot_util(d, interval, label, color1='gray', color2='red'):
    x = [x for x in d.keys()]
    y = [y for y in d.values()]
    # df = pd.DataFrame({'x': x, 'y': y}, index=pd.to_datetime(x, unit='s'))
    # df['diff'] = df['x'].diff()
    # df['w*y'] = df['diff'] * df['y']
    # # FIXME: make sure that the rolling average is calculated properly.
    # # It is a weighted average (that is an average over time calculated
    # # taking into account that the utilization stays the same between events).
    # df['rw*y'] = df['w*y'].rolling(interval).sum()
    # df['rw'] = df['diff'].rolling(interval).sum()
    # df['ry'] = df['rw*y'] / df['rw']
    # FIXME: use "step" instead of "plot"
    # xt = [dt.datetime.fromtimestamp(x) for x in x]
    plt.step(x, y, where='post', color=color1, linewidth=0.5, label=label)
    # # FIXME: make sure that the rolling average is centered properly
    # x = df['x'] - pd.Timedelta(interval).total_seconds() / 2
    # # xt = [dt.datetime.fromtimestamp(x) for x in x]
    # plt.plot(x, df['ry'], color=color2, linewidth=1, label=label)


if __name__ == "__main__":
  #Retrieve arguments
  # arguments = docopt(__doc__, version='1.0.0rc2')
  arguments, exception = docopt(__doc__, version='1.0.0rc2')

  print(arguments)

  in_file = arguments['<swf_file>']

  result = main_proc(in_file)

  print(result)