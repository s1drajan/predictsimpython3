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

slowdowns = {
    'CPLEX': 1000,
    'PureBF': 50,
    'CVH': 10,
}


def mp_worker(arg):
    # print("Running with parameters: {}".format(arg[0]))
    return parse_and_run_simulator(arg[0], arg[1])


def scs_from_dirs(sources, configs, output_folder, output_filename_template="{}___{}.swf"):
    # add sizes of sources
    ss = [(os.path.getsize(name), name) for name in sources]
    # add slowdowns of configs
    cs = []
    for name in configs:
        slowdown = 1
        for key in slowdowns:
            if key in name:
                slowdown *= slowdowns[key]
        cs.append((slowdown, name))
    scs = []
    for s_sld, s_name in ss:
        for c_sld, c_name in cs:
            scs.append((s_sld*c_sld,
                        s_name,
                        c_name,
                        os.path.join(output_folder,
                                     output_filename_template.format(os.path.basename(s_name).split('.')[0],
                                                                     os.path.basename(c_name).split('.')[0]))))
    scs.sort(reverse=True)
    return [(s_name, c_name, o_name) for _, s_name, c_name, o_name in scs]



def scs_from_file(filename):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        scs = list(reader)
    return scs


def run_batch_list(n_workers, scs, with_progress_freq=None):
    args = []
    exception = Exception
    for s_name, c_name, o_name in scs:
        config = {}
        execfile(c_name, config)
        del config['__builtins__']
        config["input_file"] = s_name
        config["output_swf"] = o_name
        config["stats"] = False
        # python 3: exec(open("example.conf").read(), config)
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
    subparsers = parser.add_subparsers()
    parser_glob = subparsers.add_parser('d', help='experiments are defined with a set of globs/dirs')
    parser_glob.add_argument('source_glob', help="glob/dir of source files (.swf)")
    parser_glob.add_argument('config_glob', help="glob/dir of config files (.py)")
    parser_glob.add_argument('output_folder', help="folder for the result files (.swf)")
    parser_glob.add_argument('--makefile', type=str,
                             help="create csv file (fith given filename) that define experiments (do not run experiments)")
    parser_file = subparsers.add_parser('f', help='experiments are defined in a csv file')
    parser_file.add_argument('filename', help='csv file that defines experiments')
    args = parser.parse_args()

    is_dry = args.dry
    num_processes = args.processes

    if hasattr(args, 'filename'):
        # reading experiments from filename
        scs = scs_from_file(args.filename)
    else:
        source_glob = args.source_glob
        if os.path.isdir(source_glob):
            sources = glob.glob(os.path.join(source_glob, "*.swf"))
        else:
            sources = glob.glob(source_glob)
            sources = [s for s in sources if s.endswith('.swf')]
        conf_glob = args.config_glob
        if os.path.isdir(conf_glob):
            configs = glob.glob(os.path.join(conf_glob, "*.py"))
        else:
            configs = glob.glob(conf_glob)
            configs = [s for s in configs if s.endswith('.py')]
        output_folder = args.output_folder
        scs = scs_from_dirs(sources, configs, output_folder)
        if args.makefile is not None and not is_dry:
            # write to file; don't run
            with open(args.makefile, 'wb') as f:
                writer = csv.writer(f)
                writer.writerows(scs)
            exit()
    if is_dry:
        print(*scs, sep='\n')
    else:
        run_batch_list(num_processes, scs, with_progress_freq=args.progress_freq)