from common import Scheduler, CpuSnapshot, list_copy 
from pyss.base.prototype import JobStartEvent, RunSchedulerEvent

class EasyBackfillScheduler(Scheduler):

    def __init__(self, options):
        super(EasyBackfillScheduler, self).__init__(options)
        self.cpu_snapshot = CpuSnapshot(self.num_processors, options["stats"])
        self.unscheduled_jobs = []
        self.run_already_scheduled = False
        # print("EasyBackfillScheduler")

    def new_events_on_job_submission(self, just_submitted_job, current_time):
        """ Here we first add the new job to the waiting list. We then try to schedule
        the jobs in the waiting list, returning a collection of new termination events """
        # TODO: a probable performance bottleneck because we reschedule all the
        # jobs. Knowing that only one new job is added allows more efficient
        # scheduling here.
        self.cpu_snapshot.archive_old_slices(current_time)
        self.unscheduled_jobs.append(just_submitted_job)

        # return self.schedule_run_if_needed(current_time) # TODO: investigate why this line has a different effect than the code below
        if (self.cpu_snapshot.free_processors_available_at(current_time) >= just_submitted_job.num_required_processors):
            return self.schedule_run_if_needed(current_time)
        else:
            return []

    def new_events_on_job_termination(self, job, current_time):
        """ Here we first delete the tail of the just terminated job (in case it's
        done before user estimation time). We then try to schedule the jobs in the waiting list,
        returning a collection of new termination events """
        self.cpu_snapshot.archive_old_slices(current_time)
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return self.schedule_run_if_needed(current_time)

    def schedule_run_if_needed(self, current_time):
        if self.run_already_scheduled:
            # print("no need to schedule")
            return []
        else:
            # print("scheduling scheduling")
            self.run_already_scheduled = True
            return [RunSchedulerEvent(current_time, None)]

    def run_scheduler(self, current_time):
        self.run_already_scheduled = False
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]

    def _schedule_jobs(self, current_time):
        "Schedules jobs that can run right now, and returns them"
        jobs = self._schedule_head_of_list(current_time)
        jobs += self._backfill_jobs(current_time)
        return jobs

    def _schedule_head_of_list(self, current_time):     
        result = []
        while True:
            if len(self.unscheduled_jobs) == 0:
                break
            # Try to schedule the first job
            if self.cpu_snapshot.free_processors_available_at(current_time) >= self.unscheduled_jobs[0].num_required_processors:
                job = self.unscheduled_jobs.pop(0)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
            else:
                # first job can't be scheduled
                break
        return result

    def _backfill_jobs(self, current_time):
        """
        Find jobs that can be backfilled and update the cpu snapshot.
        DEPRECATED FUNCTION !!!!!!
        """
        if len(self.unscheduled_jobs) <= 1:
            return []
        
        result = []
        tail_of_waiting_list = list_copy(self.unscheduled_jobs[1:])
        first_job = self.unscheduled_jobs[0]
        starttime = self.cpu_snapshot.assignJobEarliest(first_job, current_time)
        
        job_max_procs = first_job.num_required_processors
        job_max_runtime = first_job.predicted_run_time
        
        for job in tail_of_waiting_list:
            if job.predicted_run_time >= job_max_runtime and job.num_required_processors >= job_max_procs:
                 continue
            if self.cpu_snapshot.canJobStartNow(job, current_time):
                job.is_backfilled = 1
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
            else:
                if job.predicted_run_time <= job_max_runtime and job.num_required_processors <= job_max_procs:
                    job_max_procs = job.num_required_processors
                    job_max_runtime = job.predicted_run_time
        
        self.cpu_snapshot.unAssignJob(first_job)

        return result