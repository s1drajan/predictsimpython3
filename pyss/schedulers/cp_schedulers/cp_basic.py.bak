'''

Created by Alexander Goponenko at 9/7/2021


NOTE: "nodes" and "processors" are treated as they are a same thing
'''
from __future__ import division

from sortedcontainers import SortedSet
from ortools.constraint_solver import pywrapcp

from ..comod20.resources import Resource
from ..comod20.usage_tracker import UsageTracker
from ..comod20.job_pool import JobPool

from pyss.base.prototype import JobStartEvent, RunSchedulerEvent
from ..common import Scheduler


class SchedulingException(Exception):
  """Exception raised when the scheduler cannot do what it attempts.

  Attributes:
      message -- explanation of the error
  """
  pass



class ConstrProgScheduler(Scheduler):

  I_NEED_A_PREDICTOR = True

  def __init__(self, options):
    super(ConstrProgScheduler, self).__init__(options)
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
    self.timelimit = options["scheduler"].get("scheduling_timelimit", 1) * 1000


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

    solver = pywrapcp.Solver('scheduler')
    # We will search for a solution in time interval from 0 to max_makespan.
    # We will calculate max_makespan as max("durations of running job") + sum("durations of queued jobs").
    # This is just an initial assignment.
    max_makespan = 1
    queued_job_dict = {}   # dictionary key: (job, interval_var, resource_demand)
    interval_list = []
    resource_list = []

    # process running jobs
    for job in self.jobs.get_running_jobs():
      assert job.predicted_finish_time >= time
      assert job.predicted_finish_time > time
      # The duration must be > 1, since ORTools doesn't accept duration 0.
      remaining_duration =max(1, job.predicted_finish_time - time)
      max_makespan = max(max_makespan, remaining_duration)
      interval = solver.FixedDurationIntervalVar(0, 0, remaining_duration, False, job.id)
      # queued_job_dict[job.id] = (job, interval, job.num_required_processors)
      interval_list.append(interval)
      resource_list.append(job.num_required_processors)

    # tmp_res = []
    # cur_time = max_makespan + 200
    # for job in queue[:3]:
    #   cur_time += 100
    #   tmp_res.append((cur_time, job))
    #   cur_time += job.predicted_run_time
    # return tmp_res

    # trim queued jobs and finish calculation of maximum possible makespan
    sorted_queue = queue
    if len(sorted_queue) > self.limit_n_scheduled:
      sorted_queue = sorted_queue[1:self.limit_n_scheduled]
    for job in sorted_queue:
      max_makespan += max(1, job.predicted_run_time)



    # process queued jobs
    for job in sorted_queue:
      duration = max(1, job.predicted_run_time)
      min_start = 0
      max_start = max_makespan - duration
      interval = solver.FixedDurationIntervalVar(min_start, max_start, duration, False, job.id)
      queued_job_dict[job.id] = (job, interval, job.num_required_processors)
      interval_list.append(interval)
      resource_list.append(job.num_required_processors)

    # add job order heuristic constraints
    size_sorted_queue = sorted([(job.predicted_run_time, job.num_required_processors, job.submit_time, job.id) for job in sorted_queue])
    if len(size_sorted_queue) > 2:
      for (prev, next) in zip(size_sorted_queue[:-1], size_sorted_queue[1:]):
        if prev[0] == next[0] and prev[1] == next[1]:
          solver.AddConstraint(queued_job_dict[next[3]][1].StartExpr() >= queued_job_dict[prev[3]][1].StartExpr())


    # add resource constraint
    node_constraint =  solver.Cumulative(interval_list, resource_list, self.nodes.max, "cum_cst_nodes")
    solver.AddConstraint(node_constraint)

    # add objective
    # AWF
    # AWF = [nodes*job.predicted_run_time * (time - job.submit_time + interval.SafeEndExpr(max_makespan)) for job, interval, nodes in queued_job_dict.values()]
    AWF = [nodes*job.predicted_run_time * (time - job.submit_time + interval.EndExpr()) for job, interval, nodes in queued_job_dict.values()]
    objective_var = solver.Sum(AWF).Var()

    # ASpWAS
    # M_job = n * (F ** (p + 1) - Tw ** (p + 1))
    M1 = []
    M2 = []
    print("max_span: {}".format(max_makespan))
    for job, interval, nodes in queued_job_dict.values():
      Tw = time + interval.SafeStartExpr(max_makespan - job.predicted_run_time) - job.submit_time
      Tw = time + interval.StartExpr() - job.submit_time
      F = time + interval.SafeEndExpr(max_makespan) - job.submit_time
      F = time + interval.EndExpr() - job.submit_time
      # M1.append(nodes * (F*F - Tw*Tw))
      M1.append(nodes * job.predicted_run_time * (F + Tw))
      M2.append(nodes * (F*F*F - Tw*Tw*Tw))

    # objective_var = (solver.Sum(M1)).Var()
    # objective_var = solver.Max((solver.Max(solver.Sum(M2), 1) // solver.Sum(M1)), 1).Var()
    objective_var = solver.Sum(M2).Var()

    monitors = []
    objective_monitor = solver.Minimize(objective_var, 1)
    monitors.append(objective_monitor)

    best_monitor = solver.BestValueSolutionCollector(False)
    best_monitor.AddObjective(objective_var)
    # best_monitor.Add(list(job_vars.values()))
    best_monitor.Add(interval_list)
    monitors.append(best_monitor)

    limit = solver.TimeLimit(self.timelimit)
    monitors.append(limit)

    search_log =  solver.SearchLog(1000000000, objective_var)
    monitors.append(search_log)

    db = solver.Phase(interval_list, solver.INTERVAL_DEFAULT)
    # db = solver.HeuristicSearch(interval_list)

    is_solved = solver.Solve(db, monitors)

    # is_solved = solver.NextSolution()
    print("Solution found: {}.".format(is_solved))
    print("Objective function: {}".format(best_monitor.ObjectiveValue(0)))


    # sorting results according to the priorities
    # TODO: make it an configuration parameter
    sorted_dict_values = sorted(queued_job_dict.values(), key=lambda x: x[0].submit_time)
    result = []
    if return_plan:
      for job, interval, _ in sorted_dict_values :
        # assert interval.MustBePerformed(), "all jobs should be scheduled"
        # print("Job {}, interval: {} - {}".format(job.id, interval.StartMin(), interval.StartMax()))
        result.append((time + best_monitor.StartValue(0, interval), job))
    else:
      for job, interval, _ in sorted_dict_values :
        assert interval.MustBePerformed(), "all jobs should be scheduled"
        if interval.StartMin() == 0:
          result.append(job)

    solver.EndSearch()
    del solver
    return result

