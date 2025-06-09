'''
Number of terminated jobs vs time

Created by Alexander Goponenko

Usage:
    plot_completed_jobs.py <swf_file>

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
import math
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

    term_times = sorted(df["Submit Time"] + df["Wait Time"] + df["Run Time"])
    term_count = range(1, len(term_times)+1)


    #plot profile

    plt.plot(term_times, term_count)

    plt.title("# of terminated jobs for {}".format(os.path.basename(in_file).split('.')[0]))
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