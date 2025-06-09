"""
Created by Alexander Goponenko



NOTE: "nodes" and "processors" are treated as they are a same thing
"""

from __future__ import division

from sortedcontainers import SortedSet

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


class PureBFScheduler(Scheduler):

  I_NEED_A_PREDICTOR = True

  def __init__(self, options):
    super(PureBFScheduler, self).__init__(options)
    self.init_predictor(options)
    self.init_corrector(options)
    self.nodes = Resource(self.num_processors)
    self.jobs = JobPool()
    self.run_already_scheduled = False
    # with "running_jobs_prediction_enabled" the corrector is not functioning properly
    # and the option for the corrector should have no effect
    # but use "reqtime" for performance
    # FIXME: make this option work with corrector (probably not that easy)
    self.running_jobs_prediction_enabled = options["scheduler"].get("running_jobs_prediction_enabled", False)
    # print("running_jobs_prediction_enabled: {}".format(self.running_jobs_prediction_enabled))
    # NOTE: by default, we don't want to limit number of scheduled jobs.
    # 1000000 is very large number, in practice same as Infinity.
    self.limit_n_scheduled = options["scheduler"].get("limit_n_scheduled", 1000000)
    presorter_id = options["scheduler"].get("presorter", None)
    if presorter_id is None:
      self.presorter = sorters.sorter_none
    elif presorter_id in sorters.sorters:
      self.presorter = sorters.sorters[presorter_id]
    else:
      raise ValueError("Incorrect scheduler.presorter configuration")


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
    if len(queue) > self.limit_n_scheduled:
      queue = queue[0:self.limit_n_scheduled]
    sorted_by_nodes = SortedSet(queue, key=lambda job: job.num_required_processors)
    if not self.nodes.is_enough_available(sorted_by_nodes[0].num_required_processors):
      # not enough nodes for the smallest job
      return []
    # update predictions
    if self.running_jobs_prediction_enabled:
      for job in self.jobs.get_running_jobs():
        # NOTE: self.running_job is an alias for machine.jobs set by Simulator
        self.predictor.predict(job, time, self.running_jobs)
        # make sure that the prediction for the running jobs is not in the past
        if job.predicted_finish_time <= time:
          job.predicted_run_time = 1 + time - job.start_to_run_at_time
          assert job.predicted_finish_time == time+1, "we just set it"
    for job in queue:
      #NOTE: running_job is an alias for machine.jobs set by Simulator
      self.predictor.predict(job, time, self.running_jobs)
    sorted_queue = self.presorter(queue, time)
    queue_iter = iter(sorted_queue)
    # NOTE: we will track "minus available resources"
    #       it's a little bit of a hack
    #       so, the trackers reach zero when all resources are used
    #       we can schedule a job if trackers are below -job.req

    # previous version
    # ut = UsageTracker(-self.nodes.get_available())
    # for job in self.jobs.get_running_jobs():
    #   assert job.predicted_finish_time >= time
    #   assert job.predicted_finish_time > time
    #
    #   ut.remove_till_end(job.predicted_finish_time, job.num_required_processors)

    start_value = -self.nodes.get_available()
    sorted_run_jobs = sorted(self.jobs.get_running_jobs(), key=lambda x: x.predicted_finish_time)
    initial_usage = []
    if len(sorted_run_jobs) > 0:
      job = sorted_run_jobs[0]
      cur_value = start_value - job.num_required_processors
      cur_time = job.predicted_finish_time
      for job in sorted_run_jobs[1:]:
        if job.predicted_finish_time > cur_time:
          initial_usage.append((cur_time, cur_value))
          cur_time = job.predicted_finish_time
        cur_value = cur_value - job.num_required_processors
      initial_usage.append((cur_time, cur_value))
    ut = UsageTracker(start_value, initial_usage)

    # start scheduling
    started_jobs = []
    if return_plan:
      plan = []
    next_job = next(queue_iter, None)
    n_scheduled = 0
    while next_job is not None \
            and (return_plan or self.nodes.is_enough_available(sorted_by_nodes[0].num_required_processors)):
    # # FIXME: for speed we forfeit a chance to schedule a one-second job
    # while next_job is not None \
    #         and self.nodes.is_enough_available(sorted_by_nodes[0].num_required_processors) \
    #         and -sorted_by_nodes[0].num_required_processors > ut.value_at(time+1):
      cur_job = next_job
      next_job = next(queue_iter, None)
      sorted_by_nodes.remove(cur_job)
      n_scheduled +=1
      sched_time = ut.when_not_above(time, cur_job.predicted_run_time, -cur_job.num_required_processors)
      if sched_time == -1:
        raise SchedulingException("Job {} can never run".format(cur_job.id))

      # update usage trackers
      ut.add_usage(sched_time, sched_time + cur_job.predicted_run_time, cur_job.num_required_processors)
      # schedule job if it's time
      if return_plan:
        # noinspection PyUnboundLocalVariable
        plan.append((sched_time, cur_job))
      else:
        if sched_time <= time:
          assert sched_time == time
          rc = self.start_job(cur_job, time)
          if rc == False:
            raise SchedulingException("Job {} couldn't start at time {}. Possibly a running job exceeded its time limit".format(cur_job.id, time))

          started_jobs.append(cur_job)
        else:
          # logger.debug("Job %d will run at %f", cur_job.job_id, sched_time)
          pass
    if return_plan:
      return plan
    else:
      return started_jobs