"""
Created by Alexander Goponenko

This file defines predictor PredictorConditionalPercent.
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

See details in the class documentation.
"""
from __future__ import division
from sortedcontainers import SortedDict
from predictor import Predictor


class PredictorConditionalPercent(Predictor):
    """
    This predictor computes the prediction as a value such that no less than
    'confidence' fraction of previous results are no more that this value.
    In contrast with PredictiorTopPercent, this predictor takes into account knowledge
    that the job has not finished when the prediction is requested (if the job is running), 
    which may be a more accurate implementation of the survaval probability approach.
    The datapoints are weighted and the weights are decaying with arrival of each
    new point. The decay coefficient is controlled by the option 0<='alpha'<=1 :
        alpha = 0: no decay
        alpha = 1: only the last point counts.
    The predictor is initiated with an "artificial point" with duration equal to
    timelimit and weight controlled by option 'start_weight'.
    By default, the weights of the points are proportional to their duration.
    It can be changed with option 'use_weights'.
    """

    def __init__(self, options):
        self.recorder = {}
        # alpha is the "weight" of the new point, all the previous weights will decay, i.e. multiplied by (1-alpha)
        self.decay = 1 - options["scheduler"]["predictor"].get('alpha', 0.1)
        # "start weight" is the weight of the first "artifical" point, equal to the timelimit
        self.start_weight = options["scheduler"]["predictor"].get('start_weight', 0.1)
        # This is how confident we want to be that the predicted time is enough (1 means 100% confidence)
        self.confidence = options["scheduler"]["predictor"].get('confidence', 0.97)
        # Should the points also be weighted by the actual running time?
        self.use_weights = options["scheduler"]["predictor"].get('use_weights', True)


    def predict(self, job, current_time, list_running_jobs):
        """
        Modify the predicted_run_time of a job.
        Called when a job is submitted to the system.
        """
        tag = self._tag(job)
        record = self.recorder.get(tag, None)
        if record is not None:
            # if job is running then calculate its running time
            if job in list_running_jobs:
                assert job.start_to_run_at_time is not None and job.start_to_run_at_time > 0
                time_running = current_time - job.start_to_run_at_time
            else:
                assert job.start_to_run_at_time is None or job.start_to_run_at_time == -1
                time_running = 0
            job.predicted_run_time = record.predict(time_running, self.confidence) or job.user_estimated_run_time
        else:
            job.predicted_run_time = job.user_estimated_run_time


    def fit(self, job, current_time):
        """
        Add a job to the learning algorithm.
        Called when a job end.
        """
        tag = self._tag(job)
        record = self.recorder.get(tag, None)
        if record is None:
            record = Record(job.user_estimated_run_time, self.start_weight, self.use_weights)
            self.recorder[tag] = record
        record.add(job.actual_run_time, self.decay, self.confidence, self.use_weights)
        return None


    def _tag(self, job):
        return '{}|{}|{}|{}'.format(
            job.executable_id, job.user_id, job.user_estimated_run_time, job.num_required_processors)



class Record(object):
    """
    This is currently a non-efficient straightforward implementation
    """

    def __init__(self, start_value, start_weight, use_weights):
        self.dict = SortedDict()
        point_weight = start_weight * start_value if use_weights else start_weight
        self.dict[start_value] = point_weight
        self.total_weight = point_weight

    def predict(self, time_already_running, threshold):
        """
        Predicts based on the current state
        Parameters
        ----------
        time_already_running: int
            time already passed (0 in case job not started yet)
        threshold: float
            the confidence level (we believe that our prediction is over actual value with at least this probability)

        Returns
        -------
        int or None
            predicted value (running time) or None if we can't predict (caller should use default)

        """
        times = self.dict.keys()
        weights = self.dict.values()
        last_index = len(self.dict) - 1
        # find first point above time_already_running
        cur_index = self.dict.bisect_right(time_already_running)
        threshold_weight = threshold * self.total_weight
        weight_sum = 0
        while cur_index < last_index:
            weight_sum += weights[cur_index]
            if weight_sum > threshold_weight:
                # next element is above the threshold
                return times[cur_index + 1]
            cur_index += 1
        return None

    def add(self, value, a_dec, threshold, use_weights):
        """

        Parameters
        ----------
        value: int
            new value we are adding
        a_dec: float
            exponential decay alpha parameter
        threshold: float
            the confidence level (not used here - legacy parameter that might be used again in future)
        use_weights: bool
            whether we should weigh the observations by their values

        Returns
        -------
        None
        """
        for key in self.dict:
            self.dict[key] *= a_dec
        # add new value
        point_weight = value if use_weights else 1
        if value in self.dict:
            self.dict[value] += point_weight
        else:
            self.dict[value] = point_weight
        # recalculate total weight
        self.total_weight = a_dec * self.total_weight + point_weight
