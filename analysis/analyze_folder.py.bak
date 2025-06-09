'''
Usage: python2 analyze_folder.py <input_folder> <output_file>

This script runs calculate_metrics() for each of the files (swf) in input_folder
and creates a table of with metrics for all the files.

NOTE: the filenames in input_folder must have "___" (triple underscore)
that separate data label and configuration label.

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

Created by Alexander Goponenko at 3/31/2021

'''
import sys
import os
import glob
import argparse
import calculate_metrics as metrics
from table_log import TableLog

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate metrics for all swf files in input directory")
    parser.add_argument('--trim', action='store_true',
                        help="determines if data are trimmed \
                              (to reduce warmup and cooldown effects; see calculate_metrics)")
    parser.add_argument('input_files', help="directory to process")
    parser.add_argument('out_file', help="name of the output file which contains metrics in csv format")
    args = parser.parse_args()
    input_files = glob.glob(os.path.join(args.input_files, "*.swf"))
    input_files.sort()
    print (input_files)
    output = TableLog(args.out_file)
    header = ['data', 'config'] + metrics.get_header()
    print(header)
    output.log(header)
    for file in input_files:
        print("analyzing {}".format(os.path.basename(file)))
        data, config = os.path.basename(file).split('___')
        config = config.split('.')[0]
        res = metrics.calculate_metrics(file, notrim=not args.trim)
        output.log([data, config] + res)
        

