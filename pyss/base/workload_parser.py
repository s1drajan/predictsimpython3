#! /usr/bin/env python2.4

# A parser for parallel workloads in the Standard Workload Format.
#
# Information on the format and sample workloads are available at
# the Parallel Workloads Archive:
#
# http://www.cs.huji.ac.il/labs/parallel/workload/
# job type identification 
SWF_DEFAULT_PARAMS = 18
JOB_TYPE_DEFAULT = 0
JOB_TYPE_SWFFT = 1
JOB_TYPE_NEKBONE = 2
JOB_TYPE_EXAMINIMDSNAP = 3

job_params_map = {
    JOB_TYPE_DEFAULT: [],
    JOB_TYPE_SWFFT: [
    #NOTE: error is typically null but since its at the start the extra space to seperate DEFAULT from PARAMS
    # merges together leading to us having to null it out (same logic behind nekbone)
    # ('error',str),
    ('n_repetitions', int),
    ('ngx', int),
    ('ngy', int),
    ('ngz', int),
    ('nodes', int),
    ('tasks', int),
],
    JOB_TYPE_NEKBONE: [
    # ('error',str),
    ('iel0', int),
    ('ielN', int),
    ('ifbrick', str),  # could be mapped to bool with special handling for Fortran-style '.false.'
    ('istep', int),
    ('mx', int),
    ('my', int),
    ('mz', int),
    ('nodes', int),
    ('npx', int),
    ('npy', int),
    ('npz', int),
    ('nstep', int),
    ('nx0', int),
    ('nxN', int),
    ('tasks', int),
],
    JOB_TYPE_EXAMINIMDSNAP: [
    ('comm_exchange_rate', int),
    ('comm_newton', str),
    ('dt', float),
    ('error', str),
    # ('force_cutoff', str), null in our params so it is cut out
    ('force_type', str),
    ('lattice', str),
    ('lattice_constant', float),
    ('lattice_nx', int),
    ('lattice_ny', int),
    ('lattice_nz', int),
    ('lattice_offset_x', float),
    ('lattice_offset_y', float),
    ('lattice_offset_z', float),
    ('mass', float),
    ('neighbor_skin', float),
    ('nodes', int),
    ('nsteps', int),
    ('ntypes', int),
    ('tasks', int),
    ('temperature_seed', int),
    ('temperature_target', float),
    ('thermo_rate', int),
    ('type', int),
    ('units', str),
]
}

# len --> type
# if we have different jobs we will want to make a more complex parser such as adding an id col
# this will work for now
len_param_map = {
    SWF_DEFAULT_PARAMS + len(job_params_map[JOB_TYPE_DEFAULT]): JOB_TYPE_DEFAULT,
    SWF_DEFAULT_PARAMS + len(job_params_map[JOB_TYPE_SWFFT]): JOB_TYPE_SWFFT,
    SWF_DEFAULT_PARAMS + len(job_params_map[JOB_TYPE_NEKBONE]): JOB_TYPE_NEKBONE,
    SWF_DEFAULT_PARAMS + len(job_params_map[JOB_TYPE_EXAMINIMDSNAP]): JOB_TYPE_EXAMINIMDSNAP 
}

class JobInput(object): 
    def __init__(self, line):
        '''
        NOTE:
        checking for default parsing. Since, these swf are old and we can't really change how they come
        we need to adapt to their style. For example "-1    1" does not parse the same as "-1 1" when we check for params
        since we are splitting on line.split(" "). 
        For our param.swf we will parse on (" ") so every space must have a meaning (no dead space unless null or \t) 
        '''

        #checking default swf file
        tmp = line.split()
        self.job_type = JOB_TYPE_DEFAULT 

        if len(tmp) == SWF_DEFAULT_PARAMS:
            self.fields = tmp
            self.params = {}
            return 

        # has params
        self.fields = line.strip().split(" ")
        self.params = self.help_parse_params()
        # x = len(self.fields)
        # print(self.fields, x, x in len_param_map)
        # exit()
        pass #assert len(self.fields) == 18

    # parses the extra params and returns a map containing (param: str, value: int)
    def help_parse_params(self):
        # print(self.fields)
        self.job_type = JOB_TYPE_DEFAULT
        param_map = {}
        field_len = len(self.fields)-1 # -1 to account for separating space from DEFAULT_PARAMS ' ' INPUT_PARAMS

        if not field_len in len_param_map:
            print("WARNING: job does not have expected number of fields, returning DEFAULT. Check workload_parser for more information",self.fields)
            return param_map
            
        self.job_type = len_param_map[field_len]

        # enumerate through params for this type of job
        START_ADJST = 19 # starting index for the first custom param (the first 18 are default swf params)
        for idx, param in enumerate(job_params_map[self.job_type]):
            # decouple tuple (key, value type)
            key, _type = param 
            param_val = self.fields[START_ADJST+idx]

            # if null 
            if param_val == ' ' or param_val == '':
                param_map[key] = None
                continue
            # write value parsed as type
            # print(param,self.fields[START_ADJST+idx])  
            param_map[key] = _type(param_val) 
        
        # print(param_map,self.job_type)
        return param_map


    # lazy access as properties, for efficiency
    @property
    def number(self):
        return int(self.fields[0])
    @property
    def submit_time(self):
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
    # @property
    # def input_params(self):
    #     if len(self.fields) > 18:
    #         return {}

    #     # grab the rest of the params
    #     return self.fields[18:]

    def __str__(self):
        return "JobInput<number=%s>" % self.number

def parse_lines(lines_iterator):
    "returns an iterator of JobInput objects"

    def _should_skip(line): # TODO: skip if runtime, num allocated processors, submit time is problematic
        return (line.lstrip().startswith(';') or (len(line.strip()) == 0)) # comment or empty line 
         

    for line in lines_iterator:
        if _should_skip(line):
            continue # skipping

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
