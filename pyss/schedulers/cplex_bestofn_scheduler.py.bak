"""

Created by Alexander Goponenko at 9/5/2023


NOTE: "nodes" and "processors" are treated as they are a same thing
"""
from __future__ import division

import csv
import os
import sys
import traceback
from sortedcontainers import SortedSet
import docplex.cp.model as dcpm

from .comod20.resources import Resource
from .comod20.usage_tracker import UsageTracker
from .comod20.job_pool import JobPool

from pyss.base.prototype import JobStartEvent, RunSchedulerEvent
from .common import Scheduler
from . import sorters


class SchedulingException(Exception):
  """Exception raised when the scheduler cannot do what it attempts.

  Attributes:
      message -- explanation of the error
  """
  pass


class Peekable:
  def __init__(self, iterable):
    self.iter = iter(iterable)
    self.next_value = next(self.iter, None)
  
  def next(self):
    if self.next_value is None:
      return None
    else:
      result = self.next_value
      self.next_value = next(self.iter, None)
      return result
    
  def peek(self):
    return self.next_value





class CplexBestofnScheduler(Scheduler):
  """
  NOTE: Checkpointing assumptions:
  - it is not a checkpointing but rather a journaling with fast forward of the scheduling decisions
  - the predictor will receive the same events during job submission events and the job termination events, but may not receive "predict" events during the fast forward phase; it should not be affected by this
  """

  I_NEED_A_PREDICTOR = True

  KNOWN_OBJECTIVE_FUNCTIONS = [
    'ASpWAS',
    'AWF',
    'AF',
    'BSLD',
  ]

  def __init__(self, options):
    super(CplexBestofnScheduler, self).__init__(options)
    self.init_predictor(options)
    self.init_corrector(options)
    self.nodes = Resource(self.num_processors)
    self.jobs = JobPool()
    self.run_already_scheduled = False
    self.rewinding_checkpoint = False
    # with "running_jobs_prediction_enabled" the corrector is not functioning properly
    # and the option for the corrector should have no effect
    # but use "reqtime" for performance
    # FIXME: make this option work with corrector (probably not that easy)
    # self.running_jobs_prediction_enabled = options["scheduler"].get("running_jobs_prediction_enabled", False)
    self.running_jobs_prediction_enabled = False
    # NOTE: limiting number of scheduled jobs may create problems when comparing alternative schedules
    # self.limit_n_scheduled = options["scheduler"].get("limit_n_scheduled", 100)
    self.timelimit = options["scheduler"].get("scheduling_timelimit", 1)
    self.objective_function = options["scheduler"].get("objective_function", self.KNOWN_OBJECTIVE_FUNCTIONS[0])
    if self.objective_function not in self.KNOWN_OBJECTIVE_FUNCTIONS:
      raise ValueError("Incorrect scheduler.objective_function configuration")
    presorter_ids = options["scheduler"].get("alternative_presorter", None)
    self.presorters = {}
    if presorter_ids is not None:
      for presorter_id in presorter_ids:
        if presorter_id not in sorters.sorters:
          raise ValueError("Incorrect scheduler configuration: unknown presorter id '{}'".format(presorter_id))
        self.presorters[presorter_id] = {
          'func': sorters.sorters[presorter_id], 
          'count': 0
        }
    self.use_checkpointing = bool(options.get("use_checkpointing", False))
    if self.use_checkpointing:
      self.checkpointing_file = options["output_swf"] + ".checkpointing"
      self.saved_check_file = self.checkpointing_file + ".saved"
      try:
        if not os.path.isfile(self.saved_check_file):
          if os.path.isfile(self.checkpointing_file):
            os.rename(self.checkpointing_file, self.saved_check_file)
          else:
            raise Exception("checkpointing file don't exist")
        with open(self.saved_check_file, 'rb') as read_obj:
          # Return a reader object which will
          # iterate over lines in the given csvfile
          csv_reader = csv.reader(read_obj)
          # read all file
          list_of_csv = [(int(time), int(id)) for (time, id) in list(csv_reader)]
          self.checkpointing_peekable = Peekable(list_of_csv)
          self.rewinding_checkpoint = True
        print("Rewinding initialized")
      except Exception as e:
        print("Rewinding not done: " + str(e))
        self.rewinding_checkpoint = False
      try:
        os.remove(self.checkpointing_file)
      except Exception:
        pass
    if self.objective_function not in self.KNOWN_OBJECTIVE_FUNCTIONS:
      raise Exception("unknown objective function '" + str(self.objective_function) + "'")
    if self.objective_function == 'BSLD':
      self.BSLD_bound = options["scheduler"].get("BSLD_bound", 10)
    if self.objective_function == 'ASpWAS':
      # TODO: implement
      self.ASpWAS_p = 2
    sys.stdout.flush()

  def new_events_on_job_termination(self, job, current_time):
    self.finish_job(job)
    self.predictor.fit(job, current_time)
    if self.corrector.__name__ == "ninetynine":
      self.pestimator.fit(job.actual_run_time / job.user_estimated_run_time)
    return self.schedule_run_if_needed(current_time)


  def new_events_on_job_submission(self, job, current_time):
    self.submit_job(job)
    self.predictor.predict(job, current_time, self.running_jobs)
    job.initial_prediction = job.predicted_run_time
    return self.schedule_run_if_needed(current_time)


  def new_events_on_job_under_prediction(self, job, current_time):
    pass  # assert job.predicted_run_time <= job.user_estimated_run_time

    if not hasattr(job, "num_underpredict"):
      job.num_underpredict = 0
    else:
      job.num_underpredict += 1

    if self.corrector.__name__ == "ninetynine":
      new_predicted_run_time = self.corrector(self.pestimator, job, current_time)
    else:
      new_predicted_run_time = self.corrector(job, current_time)

    # set the new predicted runtime
    job.predicted_run_time = new_predicted_run_time

    # FIXME: why do we need to send this event? Should work fine without it (the event seems to be ignored anyway).
    return [JobStartEvent(current_time, job)]


  def schedule_run_if_needed(self, current_time):
    if self.run_already_scheduled:
      return []
    else:
      self.run_already_scheduled = True
      return [RunSchedulerEvent(current_time, None)]


  def run_scheduler(self, current_time):
    self.run_already_scheduled = False
    return [
      JobStartEvent(current_time, job)
      for job in self._schedule_jobs(current_time)
    ]


  def submit_job(self, job):
    self.jobs.add_pending(job)


  def start_job(self, job, current_time):
    rc = self.nodes.is_enough_available(job.num_required_processors)
    if rc:
      self.nodes.claim(job.num_required_processors)
      job.start_to_run_at_time = current_time
      self.jobs.move_to_running(job)
      if self.use_checkpointing:
        with open(self.checkpointing_file, 'ab') as f:
          w = csv.writer(f)
          w.writerow([current_time, job.id])
    return rc


  def finish_job(self, job):
    self.nodes.release(job.num_required_processors)
    self.jobs.remove_from_running(job)


  def _stop_rewinding(self):
    self.rewinding_checkpoint = False
    os.remove(self.saved_check_file)
    sys.stdout.flush()


  def _schedule_jobs(self, time, return_plan=False):
    sys.stdout.flush()
    try:
      # rewind checkpoint while possible
      # TODO: our "rewind" is acutally "fast forward" - rename as appropriate
      if self.use_checkpointing and self.rewinding_checkpoint and not return_plan:
        if self.checkpointing_peekable.peek() is None:
          print("stopped rewinding at time {}".format(time))
          self._stop_rewinding()
        elif self.checkpointing_peekable.peek()[0] < time:
          # discrepancy
          print("While rewinding checkpointing: job {} should start at {} but we are already at {}: aborting rewinding".format(
                self.checkpointing_peekable.peek()[1], self.checkpointing_peekable.peek()[0], time
          ))
          self._stop_rewinding()
        else:
          result = []
          while self.checkpointing_peekable.peek() is not None and self.checkpointing_peekable.peek()[0] == time:
            job_id = self.checkpointing_peekable.peek()[1]
            found = False
            for job in self.jobs.get_pending_jobs_list():
              if job.id == job_id:
                found = True
                rc = self.start_job(job, time)
                if rc == False:
                  raise SchedulingException("Job {} couldn't start at time {}".format(job.id,time))
                result.append(job)
                break
            if not found: 
              raise Exception("job id {} is not in the list of pending jobs".format(job_id))
            print("rewinding job {} at time {}".format(job_id, time))
            self.checkpointing_peekable.next()
          return result
    except Exception as e:
      print("While rewinding checkpointing: exception \"{}\": aborting rewinding".format(
                str(e)
          ))
      self._stop_rewinding()
    # we get here only if we are not rewinding checkpointing
    queue = self.jobs.get_pending_jobs_list()
    if len(queue) == 0:
      # no jobs to schedule - skipping scheduling
      return []
    sorted_by_nodes = SortedSet(queue, key=lambda job: job.num_required_processors)
    if not self.nodes.is_enough_available(sorted_by_nodes[0].num_required_processors):
      # not enough nodes for the smallest job - skipping scheduling
      return []
    if len(queue) == 1:
      # We have only one job in the queue and we know we can start it since we got so far
      job = queue[0]
      if return_plan:
        return [(time, job)]
      else:
        rc = self.start_job(job, time)
        if rc == False:
          raise SchedulingException(
            "Job {} couldn't start at time {}. Possibly a running job exceeded its time limit".format(job.id,
                                                                                                      time))
        return [job]
    # update predictions of running jobs
    if self.running_jobs_prediction_enabled:
      for job in self.jobs.get_running_jobs():
        # NOTE: self.running_job is an alias for machine.jobs set by Simulator
        self.predictor.predict(job, time, self.running_jobs)
        # make sure that the prediction for the running jobs is not in the past
        if job.predicted_finish_time <= time:
          job.predicted_run_time = 1 + time - job.start_to_run_at_time
          assert job.predicted_finish_time == time+1, "we just set it"
    # update predictions of queued jobs
    for job in queue:
      #NOTE: running_job is an alias for machine.jobs set by Simulator
      self.predictor.predict(job, time, self.running_jobs)

    # if len(queue) > self.limit_n_scheduled:
    #   print("Warning: at time {} queue length was {} (more than limit_n_scheduled {}}: results may be unexpected".format(
    #         time, len(queue), self.limit_n_scheduled))

    # First produce a plan with Constraint Programming.
    cp_plan = self._cp_scheduling_plan(queue, time)

    plans = []
    plan = None
    if cp_plan:
      plan = sorted(cp_plan, key=lambda x: (x[0], x[1].id))
      plans.append(plan)
    
    for alt in self.presorters:
      # Get an alternative plan.
      alt_plan = self._purebf_scheduling_plan(queue, time, self.presorters[alt]['func'])
      # choose the best
      if not alt_plan:
        # we have nothing to choose from
        print("WARNING: no alternative solution for {} at time {}".format(alt, time))
        continue
      alt_plan = sorted(alt_plan, key=lambda x: (x[0], x[1].id))
      for prev_plan in plans:
        if prev_plan == alt_plan:
          # we already have this plan, no need to process it
          continue
      plans.append(alt_plan)
      if not plan or self._measure_quality(alt_plan) < self._measure_quality(plan):
        plan = alt_plan
        # print("INFO: alternative solution was better at time {}".format(time))
      # improve on the alternative plan
      alt_cp_plan = self._cp_scheduling_plan(queue, time, alt_plan)
      if not alt_cp_plan:
        continue
      alt_cp_plan = sorted(alt_cp_plan, key=lambda x: (x[0], x[1].id))
      for prev_plan in plans:
        if prev_plan == alt_cp_plan:
          # we already have this plan, no need to process it
          continue
      # NOTE: we don't add the plan to the list of plans as it is an improved alternative
      #       and we don't want to deny another alternative an opportunity to improve
      # plans.append(alt_cp_plan)
      if self._measure_quality(plan) > self._measure_quality(alt_cp_plan):
        plan = alt_cp_plan

    if return_plan:
      return plan
    
    # start jobs if we don't return the plan
    result = []
    if not plan:
      return result
    for start_time, job in plan:
      if start_time <= time:
        rc = self.start_job(job, time)
        if rc == False:
          raise SchedulingException(
            "Job {} couldn't start at time {}. Possibly a running job exceeded its time limit".format(job.id,
                                                                                                      time))
        result.append(job)
    return result
     

  def _measure_quality(self, plan):
    # NOTE: we assume that both plans have the same set of jobs
    if self.objective_function == 'AF':
      # NOTE: we measure the sum of wait times
      return sum((time - job.submit_time for time, job in plan))
    if self.objective_function == 'AWF':
      # NOTE: we measure the weighted sum of wait times (not normalized)
      return sum((job.num_required_processors * job.predicted_run_time * (time - job.submit_time) for time, job in plan))
    if self.objective_function == 'BSLD':
      # NOTE: we measure the sum of the slowdowns (not normalized)
      return sum((max(1,(time + job.predicted_run_time - job.submit_time) / max(self.BSLD_bound, job.predicted_run_time)) 
                  for time, job in plan))
    if self.objective_function == 'ASpWAS':
      if self.ASpWAS_p != 2:
        raise NotImplementedError("ASpWAS with p != 2 is not implemented")
      M2 = []
      M3 = []
      for time, job in plan:
        Tw = time - job.submit_time
        F = Tw + job.predicted_run_time
        nodes = job.num_required_processors
        M2.append(nodes * (F ** 3 - Tw ** 3))
        M3.append(nodes * (F ** 4 - Tw ** 4))
      return (float(sum(M3)) / float(sum(M2)))
    raise NotImplementedError("Quality measure for objective function {} is not implemented".format(self.objective_function))


  def _cp_scheduling_plan(self, queue, time, initial_plan=None):
    for timelimit, verbosity in (
            # (self.timelimit, 'Normal' if initial_plan else 'Quiet'),
            (self.timelimit, 'Quiet'),
            (self.timelimit*2, 'Normal')
    ):
      try:
        return self._cp_scheduling_attempt(queue, time, timelimit, verbosity, initial_plan)
      except Exception as e:
        print("==========================================================================================")
        print("Exception during scheduling at time {}".format(time))
        print(traceback.format_exc())
        print("==========================================================================================")
        if type(e) is SchedulingException:
          raise e
    # we can get here only if all attempts failed
    return None

  
  def _cp_scheduling_attempt(self, queue, time, timelimit, verbosity, initial_plan=None):
    in_debug = verbosity == 'Normal'
    mdl = dcpm.CpoModel()
    # We will search for a solution in time interval from 0 to max_makespan.
    # We will calculate max_makespan as max("durations of running job") + sum("durations of queued jobs").
    # This is just an initial assignment.
    max_makespan = 1
    queued_job_dict = {}  # dictionary key: (job, interval_var, resource_demand, start_var, end_var)
    interval_list = []
    resource_list = []
    if in_debug:
      print("========================================================================================")
      print("Scheduling at time {}".format(time))
      print("{} running jobs and {} waiting jobs".format(len(self.jobs.get_running_jobs()), len(queue)))
    # process running jobs
    for job in self.jobs.get_running_jobs():
      assert job.predicted_finish_time >= time
      assert job.predicted_finish_time > time
      # if in_debug: print("Running job {}; processors: {}; finish {}".format(job.id, job.num_required_processors,
      #                                                                       job.predicted_finish_time))
      # The duration must be > 1, since ORTools doesn't accept duration 0.
      if in_debug and job.predicted_finish_time - time < 1:
        print("adjusting finish time for job {} from {} to {}".format(job.id, job.predicted_finish_time, time+1))
      remaining_duration = max(1, job.predicted_finish_time - time)
      max_makespan = max(max_makespan, remaining_duration)
      # interval = dcpm.interval_var(start=0, size=remaining_duration, optional=False, name='R{}'.format(job.id))
      interval = (0, remaining_duration)
      interval_list.append(interval)
      resource_list.append(job.num_required_processors)
    # trim queued jobs and finish calculation of maximum possible makespan
    sorted_queue = queue
    # if len(sorted_queue) > self.limit_n_scheduled:
    #   sorted_queue = sorted_queue[1:self.limit_n_scheduled]
    for job in sorted_queue:
      max_makespan += max(1, job.predicted_run_time)
    # print("max_makespan: {}".format(max_makespan))
    # process queued jobs
    for job in sorted_queue:
      if in_debug and job.predicted_run_time < 1:
        print("adjusting run_time for job {} from {} to {}".format(job.id, job.predicted_run_time, 1))
      duration = max(1, job.predicted_run_time)
      min_start = 0
      max_start = max_makespan - duration
      # if in_debug: print(
      #   "Queue job {}; processors: {}; duration: {}; submited: {}".format(job.id, job.num_required_processors, duration,
      #                                                                     job.submit_time))
      interval = dcpm.interval_var(start=(min_start, max_start), length=duration, optional=False,
                                   name='Q{}'.format(job.id))
      queued_job_dict[job.id] = (job, interval, job.num_required_processors)
      interval_list.append(interval)
      resource_list.append(job.num_required_processors)
    # add job order heuristic constraints
    size_sorted_queue = sorted(
      [(job.predicted_run_time, job.num_required_processors, job.submit_time, job.id) for job in sorted_queue])
    if len(size_sorted_queue) > 2:
      for (prev, next) in zip(size_sorted_queue[:-1], size_sorted_queue[1:]):
        if prev[0] == next[0] and prev[1] == next[1]:
          mdl.add(dcpm.start_before_start(queued_job_dict[prev[3]][1], queued_job_dict[next[3]][1]))
    # add resource constraint
    node_constraint = (dcpm.sum([dcpm.pulse(j, n) for j, n in zip(interval_list, resource_list)]) <= self.nodes.max)
    # node_constraint = dcpm.cumul_range(dcpm.sum([dcpm.pulse(j, n) for j, n in zip(interval_list, resource_list)]), 0, self.nodes.max)
    mdl.add(node_constraint)
    # add objective function
    if self.objective_function == 'AWF':
      # AWF
      AWF = [nodes * job.predicted_run_time * (time - job.submit_time + dcpm.end_of(interval))
               for job, interval, nodes in queued_job_dict.values()]
      objective_var = dcpm.sum(AWF)
    elif self.objective_function == 'AF':
      AF = [time - job.submit_time + dcpm.end_of(interval) for job, interval, nodes in
             queued_job_dict.values()]
      objective_var = dcpm.sum(AF)
    elif self.objective_function == 'BSLD':
      BSLD = [dcpm.max(1,
                  (time - job.submit_time + dcpm.end_of(interval)) / float(max(self.BSLD_bound,job.predicted_run_time))
                 )
              for job, interval, nodes in queued_job_dict.values()]
      objective_var = dcpm.sum(BSLD)
    else: # self.objective_function == 'ASpWAS'
      # ASpWAS
      # M_job = n * (F ** (p + 1) - Tw ** (p + 1))
      # M1 = []
      M2 = []
      M3 = []
      for job, interval, nodes in queued_job_dict.values():
        Tw = float(time) + dcpm.start_of(interval) - float(job.submit_time)
        # F = float(time) + dcpm.end_of(interval) - float(job.submit_time)
        F = Tw + float(job.predicted_run_time)
        # M1.append(nodes * (F*F - Tw*Tw))
        # M1.append(nodes * job.predicted_run_time * (F + Tw))
        # M2.append(nodes * (F*F*F - Tw*Tw*Tw))
        M2.append(nodes * (F ** 3 - Tw ** 3))
        M3.append(nodes * (F ** 4 - Tw ** 4))
      # objective_var = dcpm.sum(M2)
      # objective_var = dcpm.sum(M2) / dcpm.sum(M1)
      objective_var = dcpm.sum(M3) / dcpm.sum(M2)
    objective_monitor = dcpm.minimize(objective_var)
    mdl.add(objective_monitor)
    # res = mdl.solve(TimeLimit=self.timelimit, LogVerbosity='Normal', SearchType='IterativeDiving')
    if initial_plan:
      stp = mdl.create_empty_solution()
      for start_time, job in initial_plan:
        if job.id in queued_job_dict:
          stp.add_interval_var_solution(queued_job_dict[job.id][1], start=max(0, start_time-time))
        else:
          print("Warning: on time {} job {} was in alternative schedule but not in its optimization: results unpredicted")
      mdl.set_starting_point(stp)
    res = mdl.solve(TimeLimit=timelimit, LogVerbosity=verbosity, RelativeOptimalityTolerance=0, OptimalityTolerance=1e-8)
    # print(res)
    # sorting results according to the priorities
    # TODO: make it an configuration parameter
    sorted_dict_values = sorted(queued_job_dict.values(), key=lambda x: x[0].submit_time)
    result = []
    for job, interval, _ in sorted_dict_values:
      result.append((time + res.get_var_solution(interval).get_start(), job))
    del res
    del mdl
    return result


  def _purebf_scheduling_plan(self, queue, time, sorter):
    sorted_queue = sorter(queue, time)
    queue_iter = iter(sorted_queue)
    # NOTE: we will track "minus available resources"
    #       it's a little bit of a hack
    #       so, the trackers reach zero when all resources are used
    #       we can schedule a job if trackers are below -job.req
    ut = UsageTracker(-self.nodes.get_available())
    for job in self.jobs.get_running_jobs():
      assert job.predicted_finish_time >= time
      assert job.predicted_finish_time > time
      ut.remove_till_end(job.predicted_finish_time, job.num_required_processors)

    # start scheduling
    plan = []
    next_job = next(queue_iter, None)
    while next_job is not None:
      cur_job = next_job
      next_job = next(queue_iter, None)
      sched_time = ut.when_not_above(time, cur_job.predicted_run_time, -cur_job.num_required_processors)
      if sched_time == -1:
        raise SchedulingException("Job {} can never run".format(cur_job.id))

      # update usage trackers
      ut.add_usage(sched_time, sched_time + cur_job.predicted_run_time, cur_job.num_required_processors)
      # schedule job if it's time
      plan.append((sched_time, cur_job))

    return plan
