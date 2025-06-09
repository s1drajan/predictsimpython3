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


class PredictExact(PredictBase):
  """
  This predictor only uses the most specific tag.

  NOTE: it can return None instead of prediction
  """

  def __init__(self, recorder, decays, param_list=None, sigma_factor=None, use_weights=False):
    super(PredictExact, self).__init__(recorder, decays, sigma_factor, use_weights)


  def get_tags(self, job):
    return (
      '{}|{}|{}|{}'.format(job["job_name"], job["user"], job["timelimit"], job["nodes"]),
    )


  def get_tags_names(self):
    """ Helper function useful to generate data related to the performance of the predictor

    :return: list of names that help identify the tag "king"
    """
    return (
      '{}|{}|{}|{}'.format("job", "user", "time", "node"),
    )
