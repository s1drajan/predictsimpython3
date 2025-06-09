'''
Rough plot of total node utilization based on swf file

Created by Alexander Goponenko

Usage:
    plot_utilization.py <swf_file>

 Options:
    -h, --help  Show this screen and exit.

'''

from docopt import docopt
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import progressbar
from usage_tracker import UsageTracker
import datetime as dt

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


def main_proc(in_file):
    df = pd.read_csv(in_file, sep='\s+', comment=';', header=None, names=header)
    print(df.head())

    bsld = np.maximum((df['Wait Time'] + df['Run Time']) / np.maximum(df['Run Time'], 10), 1)
    avebsld = np.average(bsld)
    print ("AVEbsld: {}".format(avebsld))

    # create profile
    ut = UsageTracker(0)
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
        start_time = row['Submit Time'] + row['Wait Time']
        end_time = start_time + row['Run Time']
        max_time = max(max_time, end_time)
        min_time = min(min_time, start_time)
        ut.add_usage(start_time, end_time, row['Number of Allocated Processors'])
        if i % 100 == 0:
          bar.update(i)
    bar.finish()
    
    d = ut.list

    del d[-1]

    #plot profile
    x = [x for x in d.keys()]
    # x = [dt.datetime.fromtimestamp(x) for x in d.keys()]
    y = [y for y in d.values()]
    # FIXME: use "step" instead of "plot"
    plt.plot(x, y)
    plt.xlim(min_time, max_time)
    # plt.xlim(dt.datetime.fromtimestamp(min_time), dt.datetime.fromtimestamp(max_time))
    plt.show()


    return 1



if __name__ == "__main__":
  #Retrieve arguments
  # arguments = docopt(__doc__, version='1.0.0rc2')
  arguments, exception = docopt(__doc__, version='1.0.0rc2')

  print(arguments)

  in_file = arguments['<swf_file>']

  result = main_proc(in_file)

  print(result)