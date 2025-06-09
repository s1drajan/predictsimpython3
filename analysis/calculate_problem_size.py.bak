'''
Rough plot of queue length based on swf file

Created by Alexander Goponenko

Usage:
    calculate_problem_size.py <swf_file>

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


def write_profile_to_file(profile, timestamps, out_file):
    with open(out_file, 'w') as f:
        f.write('timestamp,problem_size\n')
        for i in range(len(timestamps)):
            f.write('{},{}\n'.format(timestamps[i], profile.value_at(timestamps[i])))


def calculate_problem_size(in_file):
    df = pd.read_csv(in_file, sep='\s+', comment=';', header=None, names=header)
    print(df.head())

    # bsld = np.maximum((df['Wait Time'] + df['Run Time']) / np.maximum(df['Run Time'], 10), 1)
    # avebsld = np.average(bsld)
    # print ("AVEbsld: {}".format(avebsld))

    df["Start Time"] = df["Submit Time"] + df["Wait Time"]
    df["End Time"] = df["Start Time"] + df["Run Time"]

    submit_times = np.nditer(np.sort(df['Submit Time']))
    start_times = np.nditer(np.sort(df['Start Time']))
    end_times = np.nditer(np.sort(df['End Time']))

    with open(in_file + '.queue.csv', 'w') as fq, open(in_file + '.run.csv', 'w') as fr:
        fq.write('timestamp,problem_size\n')
        fr.write('timestamp,problem_size\n')
        cur_queue_size = 0
        cur_run_size = 0
        scheduler_event = False
        next_submit_time = next(submit_times, float('inf'))
        next_start_time = next(start_times, float('inf'))
        next_end_time = next(end_times, float('inf'))
        next_time = min(next_submit_time, next_start_time, next_end_time)
        while not math.isinf(next_time):
            while next_time == next_end_time:
                scheduler_event = True
                cur_run_size -= 1
                next_end_time = next(end_times, float('inf'))
            while next_time == next_submit_time:
                scheduler_event = True
                cur_queue_size += 1
                next_submit_time = next(submit_times, float('inf'))
            if scheduler_event:
                scheduler_event = False
                fq.write('{},{}\n'.format(next_time, cur_queue_size))
                fr.write('{},{}\n'.format(next_time, cur_run_size))
            while next_time == next_start_time:
                cur_queue_size -= 1
                cur_run_size += 1
                next_start_time = next(start_times, float('inf'))
            next_time = min(next_submit_time, next_start_time, next_end_time)
    return 1


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="TODO")
  parser.add_argument('input_file', help="filename")
  args = parser.parse_args()
  in_file = args.input_file

  result = calculate_problem_size(in_file)

  print(result)