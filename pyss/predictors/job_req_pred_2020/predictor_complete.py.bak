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
from predictor_base import PredictBase


class PredictComplete(PredictBase):
  """
  This predictor has 16 kind of tags, with pre-set priorities (see get_tags).
  The prediction is calculated using highest priority record that is found.
  During update of the prediction, all 16 records corresponding to the record are updated.

  NOTE: modified to exclude the base predictor
        also it can return None instead of prediction
  """

  def __init__(self, recorder, decays, param_list=None, sigma_factor=None, use_weights=False):
    # print("PC: Sigma_factor: {}".format(sigma_factor))
    super(PredictComplete, self).__init__(recorder, decays, sigma_factor, use_weights)
    # self.stat = {}
    # self.count = {}
    # self.taglen = 15
    # if param_list is None:
    #   param_list = []
    # for param in param_list:
    #   self.stat[param] = np.zeros((self.taglen, self.taglen))
    #   self.count[param] = np.zeros((self.taglen, self.taglen))


  def get_tags(self, job):
    return (
      '{}|{}|{}|{}'.format(job["job_name"], job["user"], job["timelimit"], job["nodes"]),
      '{}|{}|{}|{}'.format(job["job_name"], job["user"], job["timelimit"], ''),
      '{}|{}|{}|{}'.format(job["job_name"], job["user"], '', job["nodes"]),
      '{}|{}|{}|{}'.format(job["job_name"], job["user"], '', ''),
      '{}|{}|{}|{}'.format(job["job_name"], '', job["timelimit"], job["nodes"]),
      '{}|{}|{}|{}'.format(job["job_name"], '', job["timelimit"], ''),
      '{}|{}|{}|{}'.format(job["job_name"], '', '', job["nodes"]),
      '{}|{}|{}|{}'.format(job["job_name"], '', '', ''),

      '{}|{}|{}|{}'.format('', job["user"], job["timelimit"], job["nodes"]),
      '{}|{}|{}|{}'.format('', job["user"], job["timelimit"], ''),
      '{}|{}|{}|{}'.format('', job["user"], '', job["nodes"]),
      '{}|{}|{}|{}'.format('', job["user"], '', ''),
      '{}|{}|{}|{}'.format('', '', job["timelimit"], job["nodes"]),
      '{}|{}|{}|{}'.format('', '', job["timelimit"], ''),
      '{}|{}|{}|{}'.format('', '', '', job["nodes"]),
      # '{}|{}|{}|{}'.format('', '', '', ''),
    )


  def get_tags_names(self):
    """ Helper function useful to generate data related to the performance of the predictor

    :return: list of names that help identify the tag "king"
    """
    return (
      '{}|{}|{}|{}'.format("job", "user", "time", "node"),
      '{}|{}|{}|{}'.format("job", "user", "time", ''),
      '{}|{}|{}|{}'.format("job", "user", '', "node"),
      '{}|{}|{}|{}'.format("job", "user", '', ''),
      '{}|{}|{}|{}'.format("job", '', "time", "node"),
      '{}|{}|{}|{}'.format("job", '', "time", ''),
      '{}|{}|{}|{}'.format("job", '', '', "node"),
      '{}|{}|{}|{}'.format("job", '', '', ''),

      '{}|{}|{}|{}'.format('', "user", "time", "node"),
      '{}|{}|{}|{}'.format('', "user", "time", ''),
      '{}|{}|{}|{}'.format('', "user", '', "node"),
      '{}|{}|{}|{}'.format('', "user", '', ''),
      '{}|{}|{}|{}'.format('', '', "time", "node"),
      '{}|{}|{}|{}'.format('', '', "time", ''),
      '{}|{}|{}|{}'.format('', '', '', "node"),
      # '{}|{}|{}|{}'.format('', '', '', ''),
    )
