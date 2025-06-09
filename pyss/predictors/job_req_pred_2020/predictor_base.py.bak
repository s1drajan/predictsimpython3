"""
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

from __future__ import division

def normalizeRecord(record):
  return record if record else (0.0, 0.0, 0.0, 0.0)


class PredictBase(object):
  """
  Copied and modified from job_req_pred_2020
  TODO: refactor to fit the rest of the code

  This is an alternative predictor base class for predictiors from job_req_pred_2020

  From job_req_pred_2020:
  =======================
  The base class for other predictors.

  By itself, this predictor simply predicts every value as the average of all jobs seen so far.

  Methods
  --------
  get_tags(job) "virtual"
      makes an ordered list of all tags for the job
      Many other predictors (such as 'complete' and 'user') can be used by simply overriding
      this method

  update_param(job, param_name, avg, var)
      updates prediction given that the average resource utilization for 'param_name' of the 'job'
      is 'avg' with variance 'var'
      Updates are made for all tags for the job.

  predict_requirements( job, param, real=None)
      makes prediction for 'param' for the 'job'
  """

  def __init__(self, recorder, decays, sigma_factor=None, use_weights=False):
    """

    :param recorder: recorder used to save records
    :param decays: dictionary of exponential decays to be used for calculating predictions
    """
    self.db = recorder
    self.decays = decays
    self.sigma_factor = sigma_factor
    self.use_weights = use_weights
    # print("Base: Sigma_factor: {}".format(sigma_factor))


  def get_tags(self, job):
    """  makes an ordered list of all tags for the job

    Many other predictors (such as 'complete' and 'user') can be used by simply overriding
    this method

    :param job: the job record (usually a dataframe row or dictionary) - not used here
    :return: list of tags
    """
    return ('///',)


  def update_param(self, job, param_name, value, var=None):
    """updates prediction  for 'param_name' of the 'job'

    NOTE: new version to calculate variance

    Updates are made for all tags for the job returned by self.get_tags.

    :param job:  the job record (usually a dataframe row or dictionary)
    :param param_name: the name of the parameter to update
    :param value: the average resource utilization for the job
    :param var: the variance of the resource utilization for the job
    :return: tuple (new average, new StDev)
             which is ignored by simulator but may be useful for analysis
    """
    if var is not None:
      raise NotImplementedError()

    alpha = self.decays[param_name]
    res = None
    point_weight = value if self.use_weights else 1
    for tag in self.get_tags(job):
      pAvg, pSquare, pCount, pSum = normalizeRecord(self.db.getRecord(tag, param_name))
      nCount = point_weight + (1 - alpha) * pCount
      nSum = value * point_weight + (1 - alpha) * pSum
      nAvg = nSum / nCount
      nSquare = value*value * point_weight + (1 - alpha) * pSquare
      if nAvg * nSum / nSquare > 1.0000000001:
        print ("Problem")
        print (alpha)
        print ((pAvg, pSquare, pCount, pSum))
        print ((nAvg, nSquare, nCount, nSum))
        print (nAvg * nSum)
        print nSquare - nAvg * nSum
        assert False
      self.db.saveRecord(tag, param_name, nAvg, nSquare, nCount, nSum)
      if res is None:
        if nCount > 1:
          res = (nAvg, self._var(nAvg, nCount, nSquare, nSum)**0.5)
        else:
          res = (None, None) # FIXME: what is the best base case?
    return res or (None, None)



  def predict_requirements(self, job, param, real=None):
    """makes prediction for 'param' for the 'job'

    :param job: the job record (usually a dataframe row or dictionary)
    :param param: the name of the parameter
    :param real: real value for the job (not used here - for compatibility with 'ideal' predictor)
    :return: the predicted value
    """
    tags = self.get_tags(job)
    for tag in tags:
      res = self.db.getRecord(tag, param)
      if res:
        pAvg, pSquare, pCount, pSum = res
        if self.sigma_factor is None:
          return pAvg
        if pCount > 1:
          pVar = self._var(pAvg, pCount, pSquare, pSum)
          return pAvg + self.sigma_factor * pVar**0.5
    return None


  def _var(self, avg, count, square, pSum):
    assert count > 1, "need more than 1 measurement"
    pVar = (square - avg * pSum) / (count - 1)
    if pVar < 0:
      if pVar < -1:
        raise Exception()
      pVar = 0.0
    return pVar