'''

Plot problem size histograms for several swf files in separate subplots

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

from plot_prob_size_hist import plot_psize_hist
from calculate_problem_size import calculate_problem_size


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot histogram of problem sizes for swf files in input directory")
    parser.add_argument('input_glob', help="wildcard of swf files to process")
    args = parser.parse_args()
    input_files = glob.glob(args.input_glob)
    input_files.sort()
    print (input_files)
    n_files = len(input_files)
    # find best number of columns and rows for subplots
    n_rows = int(n_files**0.5)
    n_cols = n_files // n_rows
    if n_rows * n_cols < n_files:
        n_cols += 1
    # create figure
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 10))
    fig.subplots_adjust(wspace=.3, hspace=.3)
    row = 0
    col = 0
    for n in range(n_files):
        ax = axes[row, col]
        # if files don't exist, run the script to create them
        if not os.path.exists(input_files[n] + '.run.csv') or not os.path.exists(input_files[n] + '.queue.csv'):
            calculate_problem_size(input_files[n])
        # plot histogram for this file
        plot_psize_hist(input_files[n] + '.run.csv', input_files[n] + '.queue.csv', ax)
        ax.set_title(os.path.basename(input_files[n]))
        col += 1
        if col == n_cols:
            col = 0
            row += 1
    plt.show()

        
        

