"""

Created by Alexander Goponenko at 9/7/2021


NOTE: "nodes" and "processors" are treated as they are a same thing
"""
from __future__ import division

from sortedcontainers import SortedSet
import docplex.cp.model as dcpm

from .comod20.resources import Resource
from .comod20.usage_tracker import UsageTracker
from .comod20.job_pool import JobPool

from pyss.base.prototype import JobStartEvent, RunSchedulerEvent
from .common import Scheduler


class SchedulingException(Exception):
  """Exception raised when the scheduler cannot do what it attempts.

  Attributes:
      message -- explanation of the error
  """
  pass



class CplexBasicScheduler(Scheduler):

  I_NEED_A_PREDICTOR = True

  def __init__(self, options):
    super(CplexBasicScheduler, self).__init__(options)
    self.init_predictor(options)
    self.init_corrector(options)
    self.nodes = Resource(self.num_processors)
    self.jobs = JobPool()
    self.run_already_scheduled = False
    # with "running_jobs_prediction_enabled" the corrector is not functioning properly
    # and the option for the corrector should have no effect
    # but use "reqtime" for performance
    # FIXME: make this option work with corrector (probably not that easy)
    # self.running_jobs_prediction_enabled = options["scheduler"].get("running_jobs_prediction_enabled", False)
    self.running_jobs_prediction_enabled = False
    self.limit_n_scheduled = options["scheduler"].get("limit_n_scheduled", 100)
    self.timelimit = options["scheduler"].get("scheduling_timelimit", 1)


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
    return rc


  def finish_job(self, job):
    self.nodes.release(job.num_required_processors)
    self.jobs.remove_from_running(job)


  def _schedule_jobs(self, time, return_plan=False):
    queue = self.jobs.get_pending_jobs_list()
    if len(queue) == 0:
      # no jobs to schedule
      return []
    sorted_by_nodes = SortedSet(queue, key=lambda job: job.num_required_processors)
    if not self.nodes.is_enough_available(sorted_by_nodes[0].num_required_processors):
      # not enough nodes for the smallest job
      return []
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

    mdl = dcpm.CpoModel()
    # We will search for a solution in time interval from 0 to max_makespan.
    # We will calculate max_makespan as max("durations of running job") + sum("durations of queued jobs").
    # This is just an initial assignment.
    max_makespan = 1
    queued_job_dict = {}   # dictionary key: (job, interval_var, resource_demand, start_var, end_var)
    interval_list = []
    resource_list = []

    print("========================================================================================")
    print("Scheduling at time {}".format(time))
    # process running jobs
    for job in self.jobs.get_running_jobs():
      assert job.predicted_finish_time >= time
      assert job.predicted_finish_time > time
      print("Running job {}; processors: {}; finish {}".format(job.id, job.num_required_processors, job.predicted_finish_time))
      # The duration must be > 1, since ORTools doesn't accept duration 0.
      remaining_duration =max(1, job.predicted_finish_time - time)
      max_makespan = max(max_makespan, remaining_duration)
      # interval = dcpm.interval_var(start=0, size=remaining_duration, optional=False, name='R{}'.format(job.id))
      interval = (0, remaining_duration)
      interval_list.append(interval)
      resource_list.append(job.num_required_processors)

    # trim queued jobs and finish calculation of maximum possible makespan
    sorted_queue = queue
    if len(sorted_queue) > self.limit_n_scheduled:
      sorted_queue = sorted_queue[1:self.limit_n_scheduled]
    for job in sorted_queue:
      max_makespan += max(1, job.predicted_run_time)
    # print("max_makespan: {}".format(max_makespan))

    # process queued jobs
    for job in sorted_queue:
      duration = max(1, job.predicted_run_time)
      min_start = 0
      max_start = max_makespan - duration
      print("Queue job {}; processors: {}; duration: {}; submited: {}".format(job.id, job.num_required_processors, duration, job.submit_time))
      interval = dcpm.interval_var(start=(min_start, max_start), size=duration, optional=False, name='Q{}'.format(job.id))
      queued_job_dict[job.id] = (job, interval, job.num_required_processors)
      interval_list.append(interval)
      resource_list.append(job.num_required_processors)

    # add job order heuristic constraints
    size_sorted_queue = sorted([(job.predicted_run_time, job.num_required_processors, job.submit_time, job.id) for job in sorted_queue])
    if len(size_sorted_queue) > 2:
      for (prev, next) in zip(size_sorted_queue[:-1], size_sorted_queue[1:]):
        if prev[0] == next[0] and prev[1] == next[1]:
          mdl.add(dcpm.start_before_start(queued_job_dict[prev[3]][1], queued_job_dict[next[3]][1]))

    # add resource constraint
    total_node_profile = dcpm.sum([dcpm.pulse(j, n) for j, n in zip(interval_list, resource_list)])
    node_constraint = (total_node_profile <= self.nodes.max)
    # node_constraint = dcpm.cumul_range(dcpm.sum([dcpm.pulse(j, n) for j, n in zip(interval_list, resource_list)]), 0, self.nodes.max)
    mdl.add(node_constraint)

    # add objective
    # AWF
    AWF = [nodes*job.predicted_run_time * (time - job.submit_time + dcpm.end_of(interval)) for job, interval, nodes in queued_job_dict.values()]
    objective_var = dcpm.sum(AWF)

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
      M2.append(nodes * (F**3 - Tw**3))
      M3.append(nodes * (F**4 - Tw**4))

    # objective_var = dcpm.sum(M2)
    # objective_var = dcpm.sum(M2) / dcpm.sum(M1)
    objective_var = dcpm.sum(M3) / dcpm.sum(M2)
    objective_var = objective_var / dcpm.standard_deviation(total_node_profile)

    objective_monitor = dcpm.minimize(objective_var)
    mdl.add(objective_monitor)

    # res = mdl.solve(TimeLimit=self.timelimit, LogVerbosity='Normal', SearchType='IterativeDiving')
    res = mdl.solve(TimeLimit=self.timelimit, LogVerbosity='Normal')
    # print(res)
    # sorting results according to the priorities
    # TODO: make it an configuration parameter
    sorted_dict_values = sorted(queued_job_dict.values(), key=lambda x: x[0].submit_time)
    result = []
    if return_plan:
      for job, interval, _ in sorted_dict_values :
        result.append((time + res.get_var_solution(interval).get_start(), job))
    else:
      for job, interval, _ in sorted_dict_values :
        # print("Job {} to start at {} and end at {}".format(
        #   job.id, res.get_var_solution(interval).get_start(), res.get_var_solution(interval).get_end()))
        if res.get_var_solution(interval).get_start() == 0:
          rc = self.start_job(job, time)
          if rc == False:
            raise SchedulingException(
              "Job {} couldn't start at time {}. Possibly a running job exceeded its time limit".format(job.id,
                                                                                                        time))
          result.append(job)

    del res
    del mdl
    return result