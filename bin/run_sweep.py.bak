'''

Created by Alexander Goponenko at 10/23/2021

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
from __future__ import print_function

import argparse
import multiprocessing
import os.path
import sys
import glob
import csv

import context
from pyss.run_simulator import parse_and_run_simulator

N_STEPS = 50
EXTENT = 2.0

def make_filename(folder, template, coeff):
    return os.path.join(folder, template.format(int(coeff*1000)))


def mp_worker(arg):
    # print("Running with parameters: {}".format(arg[0]))
    return parse_and_run_simulator(arg[0], arg[1])


def scs_from_params(source, config, output_folder, output_filename_template="{}.swf"):
    # calculate step
    step = EXTENT ** (1.0/N_STEPS)
    print("step is {}".format(step))
    scs = [(source, config, 1, make_filename(output_folder, output_filename_template, 1))]
    c1 = 1.0
    c2 = 1.0
    for i in range(0, N_STEPS):
        c1 /= step
        c2 *= step
        scs.append((source, config, c1, make_filename(output_folder, output_filename_template, c1)))
        scs.append((source, config, c2, make_filename(output_folder, output_filename_template, c2)))
    return scs


def run_batch_sweep(n_workers, scs, with_progress_freq=None):
    args = []
    exception = Exception
    for s_name, c_name, coeff, o_name in scs:
        config = {}
        execfile(c_name, config)
        # python 3: exec(open("example.conf").read(), config)
        del config['__builtins__']
        config["input_file"] = s_name
        config["output_swf"] = o_name
        config["stats"] = False
        config["scheduler"]["predictor"]["predict_multiplier"] = coeff
        if with_progress_freq:
            config['scheduler']['progressfile_freq'] = with_progress_freq
        args.append((config, exception))
    # create Pool
    pool = multiprocessing.Pool(processes=n_workers)
    # start jobs
    pool.map(mp_worker, args, chunksize=1)
    pool.close()
    pool.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry', action='store_true', help="if set, the arguments will be printed and the experiments will not run")
    parser.add_argument('--processes', type=int, default=None, help="number of parallel processes")
    parser.add_argument('--progress_freq', type=int, default=None, help='if set, the "progress" option will be forced')
    parser.add_argument('source_file', help="data source file (.swf)")
    parser.add_argument('config_file', help="base config file (.py)")
    parser.add_argument('output_folder', help="folder for the result files (.swf)")
    # parser.add_argument('--makefile', type=str,
    #                          help="create csv file (fith given filename) that define experiments (do not run experiments)")
    args = parser.parse_args()

    is_dry = args.dry
    num_processes = args.processes


    source_file = args.source_file
    conf_file = args.config_file
    output_folder = args.output_folder
    scs = scs_from_params(source_file, conf_file, output_folder)
    # if args.makefile is not None and not is_dry:
    #     # write to file; don't run
    #     with open(args.makefile, 'wb') as f:
    #         writer = csv.writer(f)
    #         writer.writerows(scs)
    #     exit()
    if is_dry:
        print(*scs, sep='\n')
    else:
        run_batch_sweep(num_processes, scs, with_progress_freq=args.progress_freq)