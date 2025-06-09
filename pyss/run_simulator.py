#!/usr/bin/env python3
# encoding: utf-8

"""
Run the PySS Simulator.

Usage:
    run_simulator.py <swf_file> <config_file> <output_file> [-i] [-v] [--withprogress=<seconds>]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode at key points in script.
    --withprogress=<seconds>                       Set progress frequency
"""

from docopt import docopt
from datetime import datetime
import sys

from pyss.base.workload_parser import parse_lines
from pyss.base.prototype import _job_inputs_to_jobs
from pyss.schedulers import simulator
from pyss.schedulers.common import module_to_class
import pyss.schedulers.common_correctors


def parse_and_run_simulator(options, exception):
    if "input_file" not in options:
        raise exception("missing input file")

    input_file = sys.stdin if options["input_file"] == "-" else open(options["input_file"])

    if "num_processors" not in options:
        for line in input_file:
            if line.lstrip().startswith('; MaxProcs:'):
                options["num_processors"] = int(line.strip()[11:])
                break

    if "num_processors" not in options:
        raise exception("missing num processors")

    options.setdefault("stats", False)

    if "progressbar" not in options.get("scheduler", {}):
        options["scheduler"]["progressbar"] = sys.stdout.isatty()

    if "scheduler" not in options or "name" not in options["scheduler"]:
        raise exception("missing scheduler or scheduler name")

    my_module = options["scheduler"]["name"]
    my_class = module_to_class(my_module)

    package = __import__('pyss.schedulers', fromlist=[my_module])
    scheduler_module = getattr(package, my_module, None)
    scheduler_class = getattr(scheduler_module, my_class, None)

    if scheduler_class is None:
        print(f"Scheduler class {my_class} not found in module {my_module}.")
        return

    scheduler = scheduler_class(options)

    try:
        print("..starting simulations..")
        starttime = datetime.now()

        simulator.run_simulator(
            num_processors=options["num_processors"],
            jobs=_job_inputs_to_jobs(parse_lines(input_file), options["num_processors"]),
            scheduler=scheduler,
            output_swf=options["output_swf"],
            input_file=options["input_file"],
            no_stats=not options["stats"],
            options=options
        )

        print("\nSimulation complete.")
        print("Num of Processors:", options["num_processors"])
        print("Input file:", options["input_file"])
        print("Scheduler:", type(scheduler))
        print("Elapsed Time:", datetime.now() - starttime)

    finally:
        if input_file is not sys.stdin:
            input_file.close()


def run_simulator(input_file, config_file, output_file, exception, withprogress=0):
    config = {}
    exec(open(config_file).read(), config)  # Python 3 replacement for execfile
    config.pop('__builtins__', None)

    config["input_file"] = input_file
    config["output_swf"] = output_file

    if withprogress:
        config['scheduler']['progressfile_freq'] = int(withprogress)

    parse_and_run_simulator(config, exception)


if __name__ == "__main__":
    arguments = docopt(__doc__)
    output_file_ = arguments["<output_file>"]
    config_file_ = arguments["<config_file>"]
    input_file_ = arguments["<swf_file>"]
    withprogress = arguments.get("--withprogress")
    run_simulator(input_file_, config_file_, output_file_, Exception, withprogress)

