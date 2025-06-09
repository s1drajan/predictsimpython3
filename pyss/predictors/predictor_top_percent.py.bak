"""
Created by Alexander Goponenko

This files defines predictor PredictorTopPercent.
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


class PredictorTopPercent(Predictor):
    """
    This predictor computes the prediction as a value such that no less than
    'confidence' fraction of previous results are no more that this value.
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
           job.predicted_run_time = record.t_val
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
        return (record.t_val, 0)


    def _tag(self, job):
        return '{}|{}|{}|{}'.format(
            job.executable_id, job.user_id, job.user_estimated_run_time, job.num_required_processors)




class Record(object):

    def __init__(self, start_value, start_weight, use_weights):
        self.dict = SortedDict()
        point_weight = start_weight*start_value if use_weights else start_weight
        self.dict[start_value] = (point_weight, 0)
        self.count = 0
        self.t_pos = 0
        self.t_val = start_value
        self.over_weight = 0
        self.under_weight = 1


    def add(self, value, a_dec, threshold, use_weights):
        point_weight = value if use_weights else 1
        if value in self.dict:
            old_weight, old_count = self.dict[value]
            new_weight = point_weight + old_weight * a_dec**(self.count-old_count)
        else:
            if value < self.t_val:
                self.t_pos += 1
            new_weight = point_weight
        self.dict[value] = (new_weight, self.count)
        self.over_weight *= a_dec
        self.under_weight *= a_dec
        # update over/under weight sums and move the threshold position if needed
        if value > self.t_val:
            self.over_weight += point_weight
            while self.under_weight / (self.under_weight + self.over_weight) <= threshold:
                self.t_pos += 1
                self.t_val = self.dict.peekitem(self.t_pos)[0]
                t_weight = self._update_t_weight(a_dec)
                self.under_weight += t_weight
                self.over_weight -= t_weight
                if self.t_pos == self.count + 1:
                    # set over_weight to zero when we got to the highest point to combat error accumulation
                    # print("WARNING: predictor_top_percent: over_weight is reset")
                    self.over_weight = 0

        else:
            self.under_weight += point_weight
            if value < self.t_val:
                t_weight = self._update_t_weight(a_dec)
                while (self.under_weight - t_weight) / (self.under_weight + self.over_weight) > threshold:
                    self.under_weight -= t_weight
                    self.over_weight += t_weight
                    self.t_pos -= 1
                    self.t_val = self.dict.peekitem(self.t_pos)[0]
                    t_weight = self._update_t_weight(a_dec)
                    if self.t_pos == 0:
                        # reset under_weight to combat error accumulation
                        # print("WARNING: predictor_top_percent: under_weight is reset")
                        self.under_weight = t_weight
        self.count += 1


    def _update_t_weight(self, a_dec):
        old_weight, old_count = self.dict[self.t_val]
        new_weight = old_weight * a_dec ** (self.count - old_count)
        # print('old : ({}, {}), new: ({}, {})'.format(old_weight, old_count, new_weight, self.count))
        self.dict[self.t_val] = (new_weight, self.count)
        return new_weight
