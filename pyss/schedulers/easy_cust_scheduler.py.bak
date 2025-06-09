"""
Added by Alexander Goponenko

Customizable EASY backfill algorithm, which can be configured to EASY-SJBF and other algorithms
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
"""

from common import Scheduler, CpuSnapshot, list_copy
from pyss.base.prototype import JobStartEvent, RunSchedulerEvent
from . import sorters



class  EasyCustScheduler(Scheduler):
    """ EASY algorithm with customizable initial and  backfill orders and prediction
    """

    I_NEED_A_PREDICTOR = True

    def __init__(self, options):
        super(EasyCustScheduler, self).__init__(options)
        self.init_predictor(options)
        self.init_corrector(options)
        self.run_already_scheduled = False

        self.cpu_snapshot = CpuSnapshot(self.num_processors, options["stats"])
        self.unscheduled_jobs = []
        presorter_id = options["scheduler"].get("presorter", None)
        if presorter_id is None:
            self.presorter = sorters.sorter_none
        elif presorter_id in sorters.sorters:
            self.presorter = sorters.sorters[presorter_id]
        else:
            raise ValueError("Incorrect scheduler.presorter configuration")
        postsorter_id = options["scheduler"].get("postsorter", None)
        if postsorter_id is None:
            self.postsorter = sorters.sorter_none
        elif postsorter_id in sorters.sorters:
            self.postsorter = sorters.sorters[postsorter_id]
        else:
            raise ValueError("Incorrect scheduler.presorter configuration")


    def new_events_on_job_submission(self, job, current_time):

        self.cpu_snapshot.archive_old_slices(current_time)
        self.predictor.predict(job, current_time, self.running_jobs)
        if not hasattr(job,"initial_prediction"):
            job.initial_prediction=job.predicted_run_time
        self.unscheduled_jobs.append(job)
        # self.unscheduled_jobs = self.presorter(self.unscheduled_jobs)
        return self.schedule_run_if_needed(current_time)


    def new_events_on_job_termination(self, job, current_time):
        self.predictor.fit(job, current_time)

        if self.corrector.__name__=="ninetynine":
            self.pestimator.fit(job.actual_run_time/job.user_estimated_run_time)

        self.cpu_snapshot.archive_old_slices(current_time)
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return self.schedule_run_if_needed(current_time)


    def new_events_on_job_under_prediction(self, job, current_time):
        pass #assert job.predicted_run_time <= job.user_estimated_run_time

        if not hasattr(job,"num_underpredict"):
            job.num_underpredict = 0
        else:
            job.num_underpredict += 1

        if self.corrector.__name__=="ninetynine":
            new_predicted_run_time = self.corrector(self.pestimator,job,current_time)
        else:
            new_predicted_run_time = self.corrector(job, current_time)

        #set the new predicted runtime
        self.cpu_snapshot.assignTailofJobToTheCpuSlices(job, new_predicted_run_time)
        job.predicted_run_time = new_predicted_run_time

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


    def _schedule_jobs(self, current_time):
        "Schedules jobs that can run right now, and returns them"

        jobs  = self._schedule_head_of_list(current_time)
        jobs += self._backfill_jobs(current_time)
        return jobs


    def _schedule_head_of_list(self, current_time):
        result = []
        self.unscheduled_jobs = self.presorter(self.unscheduled_jobs, current_time)
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
        if len(self.unscheduled_jobs) <= 1:
            return []

        result = []
        first_job = self.unscheduled_jobs[0]
        tail_sorted =  self.postsorter(self.unscheduled_jobs[1:], current_time)

        self.cpu_snapshot.assignJobEarliest(first_job, current_time)

        for job in tail_sorted:
            if self.cpu_snapshot.canJobStartNow(job, current_time):
                job.is_backfilled = 1
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)

        self.cpu_snapshot.delJobFromCpuSlices(first_job)

        return result

