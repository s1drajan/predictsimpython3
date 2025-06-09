'''
This script converts "standard" output cvs file format from `analyze_folder.py` 
into a format that has separated set of columns for each datasets and also 
normalizes the metrics to the baseline metric.

This script is for convenience only.

Usage: python convert_csv.py <file_to_convert> <output_filename>

Created by Alexander Goponenko at 5/20/2021

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
import pandas as pd
from pandas.core.common import flatten
import sys
import os
import csv

baseline = 'reqtime'


def convert_csv(in_name, out_name):
    df = pd.read_csv(in_name)
    print(df.head())

    dataset = df["data"]
    l_data = sorted(dataset.unique())
    n_data = len(l_data)
    config = df[df['data'] == df['data'][0]]['config']
    # print(config)
    split_conf = config.str.split(pat='_', n=1, expand=True)
    # print(split_conf)
    l_sched = split_conf[0].unique()
    # print (l_sched)
    result = [['']] * 2 + list(map(lambda x: [x], config))
    # print(result)
    for data in l_data:
        df1 = df[df['data'] == data].drop(['data', 'config'],
                                          axis=1).reset_index(drop=True)
        # print (df[df['data']==data].head())
        # print(data)
        for sched in l_sched:
            # print(sched)
            # print(df1.loc[(split_conf[0]==sched) & (split_conf[1]==baseline), :])
            # dividing by the baseline row
            df1.loc[split_conf[0] == sched, :] = df1.loc[
                split_conf[0] == sched, :].div(
                    df1.loc[(split_conf[0] == sched) &
                            (split_conf[1] == baseline), :].values)
        # assembling results to a box
        box = [[data] * len(df1.columns)] + [df1.columns.values.tolist()
                                             ] + df1.values.tolist()
        result = list(map(lambda x: x[0] + [''] + x[1], zip(result, box)))

    # print result
    with open(out_name, 'wb') as f:
        csv.writer(f).writerows(result)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python {} <file_to_convert> <output_filename>".format(
            os.path.basename(__file__)))
        exit(1)
    in_name = sys.argv[1]
    out_name = sys.argv[2]
    convert_csv(in_name, out_name)
