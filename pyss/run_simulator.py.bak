#!/usr/bin/pypy
# encoding: utf-8
'''
Run the PySS Simulator. You should specify a config file, an enforce input and output swfs over that via commandline if you so desire.

Usage:
    run_simulator.py <swf_file> <config_file> <output_file> [-i] [-v] [--withprogress=<seconds>]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode at key points in script.
    --withprogress=<seconds>                       Force to set progress_freq option
'''
from __future__ import print_function

import context

from base.docopt import docopt
import sys

if __debug__:
    import warnings
    #warnings.warn("Running in debug mode, this will be slow... try 'python2.4 -O %s'" % sys.argv[0])

from base.workload_parser import parse_lines
from base.prototype import _job_inputs_to_jobs
import schedulers.simulator as simulator
from schedulers.common import module_to_class
import optparse
import schedulers.common_correctors

from datetime import datetime


def parse_and_run_simulator(options, exception):

  if "input_file" not in options:
    raise exception("missing input file")


  if options["input_file"] == "-":
    input_file = sys.stdin
  else:
    input_file = open(options["input_file"])

  if "num_processors" not in options:
    input_file = open(options["input_file"])
    for line in input_file:
      if(line.lstrip().startswith(';')):
        if(line.lstrip().startswith('; MaxProcs:')):
          options["num_processors"] = int(line.strip()[11:])
          break
        else:
          continue
      else:
        break
  if "num_processors" not in options:
    raise exception("missing num processors")

  if "stats" not in options:
    options["stats"] = False

  if "progressbar" not in options["scheduler"]:
    if sys.stdout.isatty():# You're running in a real terminal
      options["scheduler"]["progressbar"] = True
    else:# You're being piped or redirected
      options["scheduler"]["progressbar"] = False

  if "scheduler"  not in options:
    raise exception("missing scheduler")

  if "name" not in options["scheduler"]:
    raise exception("missing scheduler name")




  my_module = options["scheduler"]["name"]
  my_class = module_to_class(my_module)

  #load module(or file)
  package = __import__ ('schedulers', fromlist=[my_module])
  if my_module not in package.__dict__:
    print("No such scheduler (module file not found).")
    print(package.__dict__.keys())
    return
  if my_class not in package.__dict__[my_module].__dict__:
    print("No such scheduler (class within the module file not found).")
    return
  #load the class
  scheduler_non_instancied = package.__dict__[my_module].__dict__[my_class]

  scheduler = scheduler_non_instancied(options)


  #if hasattr(scheduler_non_instancied, 'I_NEED_A_PREDICTOR'):

  try:
    print("..starting simulations..")
    starttime = datetime.today()
    simulator.run_simulator(
      num_processors = options["num_processors"],
      jobs = _job_inputs_to_jobs(parse_lines(input_file), options["num_processors"]),
      scheduler = scheduler,
      output_swf = options["output_swf"],
      input_file = options["input_file"],
      no_stats = not(options["stats"]),
      options = options
      )
    # Finishing up
    print("\n")
    print("Num of Processors: ", options["num_processors"])
    print("Input file: ", options["input_file"])
    print("Scheduler:", type(scheduler))

    print("Elapsed Time:", datetime.today() - starttime)

  finally:
    if input_file is not sys.stdin:
      input_file.close()


def run_simulator(input_file, config_file, output_file, exception, withprogress=0):
  config = {}
  execfile(config_file, config)
  del config['__builtins__']
  config["input_file"] = input_file
  config["output_swf"] = output_file
  # python 3: exec(open("example.conf").read(), config)
  if withprogress:
    config['scheduler']['progressfile_freq'] = int(withprogress)
  # parse_and_run_simulator(config)
  parse_and_run_simulator(config, exception)


if __name__ == "__main__":
  #Retrieve arguments
  # arguments = docopt(__doc__, version='1.0.0rc2')
  arguments, exception = docopt(__doc__, version='1.0.0rc2') #AG+

  output_file_ = arguments["<output_file>"]
  config_file_ = arguments["<config_file>"]
  input_file_ = arguments["<swf_file>"]
  withprogress = arguments["--withprogress"]
  run_simulator(input_file_, config_file_, output_file_, exception, withprogress)

