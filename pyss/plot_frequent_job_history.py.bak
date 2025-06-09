'''

Created by Alexander Goponenko

Usage:
    plot_frequent_job_history.py <swf_file>

 Options:
    -h, --help  Show this screen and exit.

This script accepts an swf file,
splits it into dataframes so that each dataframe
contains jobs with same script, user, timelimit, and number of CPUs,
then performs prediction on each such dataframe separately
and shows separate plots of the results for each dataframe:
    current prediction over time,
    duration and timespan of each job,
    and histogram of jobs' duration.

When one plot is dismissed, another plot is shown until no more dataframes left.
It can take forever, so terminate the script manually.

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

from __future__ import division

import os.path

from base.docopt import docopt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from base.prototype import Job

header = [
    'job_id',
    'Submit Time',
    'Wait Time',
    'Run Time',
    'Number of Allocated Processors',
    'Average CPU Time Used',
    'Used Memory',
    'Requested Number of Processors',
    'Requested Time',
    'Requested Memory',
    'Status',
    'User ID',
    'Group ID',
    'Executable',
    'Queue Number',
    'Partition Number',
    'Preceding Job Number',
    'Think Time'
]

from predictors.predictor_exact import PredictorExact as Predictor
#
# options = {
#     'scheduler':{
#         'predictor':{
#
#         }
#     }
# }

# from predictors.predictor_top_percent import PredictorTopPercent as Predictor

options = {
    'scheduler':{
        'predictor':{
            'confidence': .97,
            'start_weight': 0.1,
            'use_weights': True,

        }
    }
}

def run_predictor(df):
    predictor = Predictor(options=options)
    list2 = df.sort_values(by=['End Time'])
    list2['prediction_avg'] = -1
    list2['prediction_var'] = -1
    for idx in list2.index:
        ending_job = list2.loc[idx]
        # print (ending_job)
        job = Job(
            ending_job["job_id"],
            ending_job["Requested Time"],
            ending_job["Run Time"],
            ending_job["Requested Number of Processors"],
            ending_job["Submit Time"],
            0,
            0,
            ending_job["User ID"],
            0,
            ending_job["Group ID"],
            ending_job["Executable"],
        )
        job.start_to_run_at_time = job.submit_time + ending_job["Wait Time"]

        avg, var = predictor.fit(job, job.start_to_run_at_time + job.actual_run_time)
        list2.loc[idx, 'prediction_avg'] = avg
        list2.loc[idx, 'prediction_var'] = var
    return list2


def do_main(in_file):
    df = pd.read_csv(in_file, sep='\s+', comment=';', header=None, names=header)
    df['Start Time'] = df['Submit Time'] + df['Wait Time']
    df['End Time'] = df['Start Time'] + df['Run Time']
    df['Tag'] = df[['Executable', 'User ID', 'Requested Time', 'Requested Number of Processors']].astype(str).agg(
        '|'.join, axis=1)
    counts = df.groupby('Tag').size().reset_index(name='count')
    counts = counts.sort_values(by=['count'], ascending=False)
    # print(df.head())
    for _, instance in counts.iterrows():
        print(instance)
        tag = instance['Tag']
        dff = df[df['Tag'] == tag]
        dfp = run_predictor(dff)
        # print(dfp)
        #plot results
        fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12,5), gridspec_kw={'wspace': 0.05, 'width_ratios': [10, 2]})
        limit = dfp['Requested Time'].mean()
        fig.suptitle('Dataset: {}     {} jobs with s={}  u={}  t={}  n={}'.format(
            os.path.basename(in_file).split('___')[0],
            instance['count'],
            dfp.loc[dfp.index[0], 'Executable'],
            dfp.loc[dfp.index[0], 'User ID'].astype('int'),
            dfp.loc[dfp.index[0], 'Requested Time'].astype('int'),
            dfp.loc[dfp.index[0], 'Requested Number of Processors'].astype('int')
        ))

        ax1.step(dfp['End Time'], dfp['prediction_avg'], where='post', linewidth=2, color='#777777')
        # ax.plot([dfp['Start Time'].min(), dfp['End Time'].max()], [limit] * 2, linewidth=.25, color='#777777')

        ax1.step(dfp['End Time'], np.minimum(dfp['prediction_avg'] + dfp['prediction_var'], limit), where='post', linewidth=1, color='#999999')
        ax1.step(dfp['End Time'], np.minimum(dfp['prediction_avg'] + dfp['prediction_var']*3, limit), where='post', linewidth=0.5, color='#cccccc')
        for _, job in dff.iterrows():
            ax1.plot([job['Start Time'], job['End Time']], [job['Run Time']]*2, marker='|', ms=3, linewidth=3)
        ax1.set_xlabel("timestamp / s")
        ax1.set_ylabel("duration / s")

        ax2.hist(dfp['Run Time'], bins='doane', orientation='horizontal', color='#9999ff')
        ax2.set_xlabel("count")
        plt.show()
    return "Done"




def plot_results(df):
    pass



if __name__ == "__main__":
  #Retrieve arguments
  # arguments = docopt(__doc__, version='1.0.0rc2')
  arguments, exception = docopt(__doc__, version='1.0.0rc2')

  print(arguments)

  in_file = arguments['<swf_file>']

  result = do_main(in_file)
