#! /usr/bin/env python2.4

# A parser for parallel workloads in the Standard Workload Format.
#
# Information on the format and sample workloads are available at
# the Parallel Workloads Archive:
#
# http://www.cs.huji.ac.il/labs/parallel/workload/
# job type identification 
from . import job_types
import numpy as np

PARAM_TOKEN = "params"
DROP_TOKEN = "drop_col"

SWF_DEFAULT_PARAMS = 18

SUBMIT_DIST_N = 100000
CURR_DIST_IDX = 0
SAMPLE_TIME = 1
rng = np.random.default_rng(seed=42)
dist = rng.normal(loc=1,scale=5,size=SUBMIT_DIST_N)
job_submit_dist = list(map(lambda x: (abs(x) * 100)+5, dist))

def submit_job():
    global CURR_DIST_IDX, SAMPLE_TIME, SUBMIT_DIST_N
    CURR_DIST_IDX += 1
    SAMPLE_TIME += 2
    return SAMPLE_TIME + int(job_submit_dist[CURR_DIST_IDX % SUBMIT_DIST_N])

def parse_params(line):
    line = line.strip()

    tokens = line.split(" ")
    app_id = int(tokens[0])
    params = tokens[1:]
          
    result = {}
    for idx, param_name in enumerate(job_types.param_map[app_id]):
        try:
            if params[idx] in [""," "]:    
                result[param_name] = None #null
                continue
            value = float(params[idx])
        except:
            value = str(params[idx])

        result[param_name] = value
    return result, app_id

class JobInput(object): 
    def __init__(self, line):
        '''
        NOTE:
        checking for default parsing. Since, these swf are old and we can't really change how they come
        we need to adapt to their style. For example "-1    1" does not parse the same as "-1 1" when we check for params
        since we are splitting on line.split(" "). 
        For our param.swf we will parse on (" ") so every space must have a meaning (no dead space unless null or \t) 
        '''
        self.job_type = job_types.JOB_TYPE_DEFAULT 
        self.params = {}
        self.parse_line(line=line)

    def parse_line(self,line):
        line = line.rstrip()   
        tmp = line.split("  ", maxsplit=1)
    
        tmp_size = len(tmp)
        if tmp_size == 0:
            exit("error parsing line led us to zero")
    
        default = tmp[0].rstrip().split(" ") 
        self.fields = default

        # no params skipp over
        if tmp_size == 1:
            return
    
        # we have params so parse them
        params = tmp[1]
        param_map, app_id = parse_params(line=params)

        self.params = param_map
        self.job_type = app_id

    # lazy access as properties, for efficiency
    @property
    def number(self):
        return int(self.fields[0])
    @property
    def submit_time(self):
        # return submit_job() 
        return int(self.fields[1])
    @property
    def wait_time(self):
        return int(self.fields[2])
    @property
    def run_time(self):
        return float(self.fields[3])
    @property
    def num_allocated_processors(self):
        return int(self.fields[4])
    @property
    def average_cpu_time_used(self):
        return int(self.fields[5])
    @property
    def used_memory(self):
        return int(self.fields[6])
    @property
    def num_requested_processors(self):
        result = int(self.fields[7])
        if result > 0:
            return result
        else:
            # a negative value means this is the same as the no. of allocated processors
            return self.num_allocated_processors
    @property
    def requested_time(self):
        return int(self.fields[8])
    @property
    def requested_memory(self):
        return int(self.fields[9])
    @property
    def status(self):
        return int(self.fields[10]) 
    @property
    def user_id(self):
        return int(self.fields[11])
    @property
    def group_id(self):
        return int(self.fields[12])
    @property
    def executable_number(self):
        return int(self.fields[13])
    @property
    def queue_number(self):
        return int(self.fields[14])
    @property
    def partition_number(self):
        return int(self.fields[15])
    @property
    def preceding_job_number(self):
        return int(self.fields[16])
    @property
    def think_time_from_preceding_job(self):
        return int(self.fields[17])

    def __str__(self):
        return "JobInput<number=%s>" % self.number

def parse_param_initilizer(line):
    PARAM_IDX = 3
    tokens = line.strip().split(" ") 

    token_id, app_name, app_id = tokens[:PARAM_IDX]; app_id = int(app_id)
    params = tokens[PARAM_IDX:]

    # ensure no collisions in map
    if (app_id in job_types.param_map 
        or app_id in job_types.job_ids):
        exit("failed had a collision in param_map",app_id,app_name)
 
    # setup maps
    job_types.app_name_map[app_id] = app_name
    job_types.job_ids.add(app_id)
    job_types.param_map[app_id] = params

def parse_drop_col_initilizer(line):
    COLS_IDX = 2
    tokens = line.strip().split(" ")
    
    token_id, app_id = tokens[:COLS_IDX]; app_id = int(app_id)
    drop_cols = tokens[COLS_IDX:]

    result = []

    for col in drop_cols:
        if not col in job_types.param_map[app_id]:
            print(f"WARNING DROP COLUMN \'{col}\' not in param_map [not adding]")
            continue
        result.append(col)

    job_types.drop_param_map[app_id] = result 

def parse_lines(lines_iterator):
    "returns an iterator of JobInput objects"

    def _should_skip(line): # TODO: skip if runtime, num allocated processors, submit time is problematic
        return (line.lstrip().startswith(';') or (len(line.strip()) == 0)) # comment or empty line 
    
    def _param_parse(line):
        return line.lstrip().startswith(PARAM_TOKEN)
    def _drop_col_parse(line):
        return line.lstrip().startswith(DROP_TOKEN)
         

    for line in lines_iterator:
        if _should_skip(line):
            continue # skipping

        # parse params
        if _param_parse(line):
            parse_param_initilizer(line=line)
            continue

        # parse drop column 
        if _drop_col_parse(line):
            parse_drop_col_initilizer(line=line)
            continue


        yield JobInput(line)

def _measure_performance():
    import sys
    import time
    print("reading from stdin")
    start_time = time.time()
    jobs = parse_lines(sys.stdin)
    counter = 0
    for job in jobs:
        counter += 1
    end_time = time.time()
    total_time = end_time - start_time
    print("no. of jobs:", counter)
    print("total time (seconds):", total_time)
    print("jobs per second: %3.1f" % (float(counter) / total_time))

def _test():
    job = JobInput("   59    26613      0    716   32     -1    -1   -1     -1    -1 -1   4   1   3  0 -1 -1 -1")
    pass #assert str(job).startswith("JobInput")
    pass #assert job.number == 59

if __name__ == "__main__":
    import optparse

    parser = optparse.OptionParser(usage="%prog <test/performance>")
    options, args = parser.parse_args()
    if len(args) == 0: parser.error("no action given")

    action = args[0]

    if action == "test":
        _test()
    elif action == "performance":
        _measure_performance()
    else:
        parser.error("unknown action '%s'" % action)
