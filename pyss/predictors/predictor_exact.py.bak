'''

Created by Alexander Goponenko at 4/7/2021

Not used in SBAC-PAD 2022 publication
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
'''
from job_req_pred_2020.predictsim_wrapper import PredictorWrapper
from job_req_pred_2020.predictor_exact import PredictExact as JRPBase
from job_req_pred_2020.recorder_mem import Recorder

PARAM_NAME = 'duration'

class PredictorExact(PredictorWrapper):

    def __init__(self, options):
        alpha = options["scheduler"]["predictor"].get('decay', 0.2)
        sigma_factor = options["scheduler"]["predictor"].get('sigma_factor', None)
        use_weights = options["scheduler"]["predictor"].get('use_weights', False)

        # print(options)
        # print ("sigma_factor: {}".format(sigma_factor))
        decays = {PARAM_NAME : alpha}
        recorder = Recorder()
        jrp_predictor = JRPBase(recorder, decays, [PARAM_NAME], sigma_factor, use_weights)
        super(PredictorExact, self).__init__(jrp_predictor, PARAM_NAME)