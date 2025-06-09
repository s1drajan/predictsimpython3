'''
This script makes Fig. 2-4 and 6 in DEBS2024 paper

Usage:
Create swf files and adjust file location in the script.
Then run the script.

Created by Alexander Goponenko

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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mtick


table_filename = "../results/cplex_of_plot2.csv"

metrics = ['BSLD', 'AF', 'AWF', 'P2SF']
workloads = ['KTH-SP2', 'CTC-SP2',   'SDSC-SP2',  'SDSC-BLUE',  'CEA-CURIE',  'BW201911']
# labels = {
#   'CPLEX_BSLD': '$\\bm{A} = \\textit{CP-BSLD}$',
#   'SAF-JustBF': '$\\bm{A} = \\textit{SAF-ListBF}$',
#   'SJF-JustBF': '$\\bm{A} = \\textit{SJF-ListBF}$',
#   'SRD2F-JustBF': '$\\bm{A} = \\textit{SPF-ListBF}$',
#   'CPLEX_BSLD+': '$\\bm{A} = \\textit{CP-BSLD+}$',
#   'CPLEX_off_BSLD': '$\\bm{A} = \\textit{CP-OFF-BSLD}$',
#   'CPLEX_off_AF': '$\\bm{A} = \\textit{CP-OFF-AF}$',
#   'CPLEX_AF': '$\\bm{A} = \\textit{CP-AF}$',
#   'JustBF': '$\\bm{A} = \\textit{REG-ListBF}$',
#   'LAF-JustBF': '$\\bm{A} = \\textit{LAF-ListBF}$',
#   'CPLEX_AWF': '$\\bm{A} = \\textit{CP-AWF}$',
#   'CPLEX_P2SF': '$\\bm{A} = \\textit{CP-P\\textsuperscript{\kern 0.066em2\!}SF}$',
#   'CPLEX_AWF_off': '$\\bm{A} = \\textit{CP-OFF-AWF}$',
#   'CPLEX_off_P2SF': '$\\bm{A} = \\textit{CP-OFF-P\\textsuperscript{\kern 0.066em2\!}SF}$'
# }
labels = {
  'CPLEX_BSLD': '$\\bm{A} = \\textit{CP-BSLD}$',
  'SAF-JustBF': '$\\bm{A} = \\textit{List-SAF}$',
  'SJF-JustBF': '$\\bm{A} = \\textit{List-SJF}$',
  'SRD2F-JustBF': '$\\bm{A} = \\textit{List-SPF}$',
  'CPLEX_BSLD+': '$\\bm{A} = \\textit{CP-BSLD+}$',
  'CPLEX_off_BSLD': '$\\bm{A} = \\textit{CP-OFF-BSLD}$',
  'CPLEX_off_AF': '$\\bm{A} = \\textit{CP-OFF-AF}$',
  'CPLEX_AF': '$\\bm{A} = \\textit{CP-AF}$',
  'JustBF': '$\\bm{A} = \\textit{List-REG}$',
  'LAF-JustBF': '$\\bm{A} = \\textit{List-LAF}$',
  'CPLEX_AWF': '$\\bm{A} = \\textit{CP-AWF}$',
  'CPLEX_P2SF': '$\\bm{A} = \\textit{CP-P\\textsuperscript{\kern 0.066em2\!}SF}$',
  'CPLEX_P2SF+': '$\\bm{A} = \\textit{CP-P\\textsuperscript{\kern 0.066em2\!}SF+}$',
  'CPLEX_AWF_off': '$\\bm{A} = \\textit{CP-OFF-AWF}$',
  'CPLEX_off_P2SF': '$\\bm{A} = \\textit{CP-OFF-P\\textsuperscript{\kern 0.066em2\!}SF}$'
}


styles = {
    'CPLEX_BSLD': ['....', '#7F0002', '#E8E0E0'],
    'CPLEX_BSLD+': ['OO..', '#7F0002', '#E8E0E0'],
    'SAF-JustBF': ['xxxx', '#000000', '#dddddd'],
    'SJF-JustBF': ['////', '#4472C4', '#DAE3F3'],
    'SRD2F-JustBF': ['\\\\\\\\', '#7F0002', '#FFEFEF'],
    'CPLEX_off_BSLD': ['', '#000000', '#7F0002'],
    'CPLEX_off_AF': ['', '#000000', '#000000'],
    'CPLEX_AF': ['....', '#000000', '#dddddd'],
    # 'JustBF': ['', '#aaaaaa', '#F8F0C6'],
    'JustBF': ['', '#aaaaaa', '#FFF4D6'],
    'LAF-JustBF': ['-----', '#5A8140', '#E2F0D9'],
    'CPLEX_AWF': ['....', '#5A8140', '#E2F0D9'],
    'CPLEX_P2SF': ['....', '#7F6000', '#E6E3DA'],
    'CPLEX_P2SF+': ['OO..', '#7F6000', '#E6E3DA'],
    'CPLEX_AWF_off': ['', '#000000', '#5A8140'],
    'CPLEX_off_P2SF': ['', '#000000', '#7F6000']
}

orders = {
  'BSLD': ['CPLEX_off_BSLD', 'CPLEX_BSLD+', 'CPLEX_BSLD', 'SRD2F-JustBF', 'SAF-JustBF', 'SJF-JustBF', 'JustBF'],
  'AF': ['CPLEX_off_AF', 'CPLEX_AF', 'SAF-JustBF', 'SJF-JustBF', 'JustBF'],
  'AWF': ['CPLEX_AWF_off', 'CPLEX_AWF', 'LAF-JustBF', 'JustBF'],
  'P2SF': ['CPLEX_off_P2SF', 'CPLEX_P2SF+', 'CPLEX_P2SF', 'JustBF']
}

width_adjust = {
  'BSLD': 1,
  'AF': 1,
  'AWF': 1,
  'P2SF': 1
}

legend_loc = {
  'BSLD': 'upper right',
  'AF': 'upper right',
  'AWF': 'center right',
  'P2SF': 'upper right'
}

y_title = {
  'BSLD': '$\\sfrac{\\mathit{BSLD}_{\!\!\\mathlarger{\\bm{A}}}}{\\mathit{BSLD}_{\\textit{List-REG}}}$',
  'AF': '$\\sfrac{\\mathit{AF}_{\!\!\\mathlarger{\\bm{A}}}}{\\mathit{AF}_{\\textit{List-REG}}}$',
  'AWF': '$\\sfrac{\\mathit{AWF}_{\!\!\\mathlarger{\\bm{A}}}}{\\mathit{AWF}_{\\textit{List-REG}}}$',
  'P2SF': '$\\sfrac{\\mathit{P^{2}\!SF}_{\!\!\\mathlarger{\\bm{A}}}}{\\mathit{P^{2}\!SF}_{\\textit{List-REG}}}$',
}

def color_to_zorder(color):
  # convert color to brightness
  # https://stackoverflow.com/questions/596216/formula-to-determine-brightness-of-rgb-color
  r = int(color[1:3], 16) / 256
  g = int(color[3:5], 16) / 256
  b = int(color[5:7], 16) / 256
  brightness = (r * 299 + g * 587 + b * 114)
  print("Brightness: ", brightness)
  return 1000 - brightness




def plot_metric_fig(df, metric, order_metric, save=None, legend=True, bbox_to_anchor=None):
  order = orders[order_metric]
  x = np.arange(len(workloads), dtype=float)
  width = 1 / (len(order) - width_adjust[order_metric] + 1)
  shift = -width * width_adjust[order_metric]
  print (df.head())
  matplotlib.rc('text', usetex=True)
  matplotlib.rc(
      'text.latex',
      # libertine and newtxmath are for ACM style
      preamble='\\usepackage{bm} \\usepackage{xfrac} \\usepackage{relsize} \\usepackage{libertine} \\usepackage[libertine]{newtxmath}'
  )
  matplotlib.rc('hatch', linewidth=1.0)
  # matplotlib.rc('mathtext', fontset='newtxmath')
  # set dpi
  plt.rcParams['figure.dpi'] = 300

  fig, ax = plt.subplots(1, 1, figsize=(8, 4))
  for alg in order:
    print("Processing ", alg)
    alg_df = df[df['scheduler'] == alg]
    m_df = alg_df[alg_df['metric'] == metric]
    y = [m_df[wl].iloc[0] for wl in workloads]
    # add a histogram to the plot with a given shift and width and color
    h, ec, c = styles[alg]
    ax.bar(x + shift, y, label=labels[alg], width=width, zorder=color_to_zorder(ec), hatch=h, edgecolor=ec, color=c, linewidth=1.5, rasterized=True)
    shift += width
  ax.set_xlim(-width * (1+width_adjust[order_metric]), len(workloads) - width)
  # set x-ticks
  ## adjust first x-tick
  x[0] -= width * width_adjust[order_metric]/2
  # print(x)
  wl_labels = ["\\textit{{{}}}".format(wl) for wl in workloads]
  # wl_labels = workloads
  ax.set_xticks(x + 0.5 - width, wl_labels, fontsize='13')
  # don't show x-ticks
  ax.tick_params(axis='x', which='both', bottom=False, top=False)
  # set y-tikcs as percentages
  ax.tick_params(axis='y', labelsize=13)
  ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
  # vals = ax.get_yticks()
  # ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals], fontsize='11')
  # show y grid behind the bars
  ax.grid(axis='y', zorder=0, color='#eeeeee')

  ax.set_ylabel(y_title[metric], fontsize='18')
  # ax.set_xlabel('Workload')
  if legend:
    if isinstance(legend, str):
      loc = legend
    else:
      loc = legend_loc[metric]
    if bbox_to_anchor:
      leg = ax.legend(loc=loc, handlelength=1.5, handleheight=1.1, fontsize='13', framealpha=1, borderaxespad=0, bbox_to_anchor=bbox_to_anchor)
    else:
      leg = ax.legend(loc=loc, handlelength=1.5, handleheight=1.1, fontsize='13', framealpha=1, borderaxespad=0)
    leg.set_zorder(1100)
    # leg2 = ax.legend(loc="center", handlelength=1.5, handleheight=1.1, fontsize='13', framealpha=1, borderaxespad=0)
    # ax.add_artist(leg)
    leg.get_frame().set_edgecolor('black')
    # rasterize patches
    # for patch in leg.get_patches():
    #   patch.set_rasterized(True)
    leg.set_rasterized(True)
    # # increase font size
    # for text in leg.get_texts():
    #   text.set_fontsize('large')
    # remove top and right borders
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  # set z-order for axes
  ax.spines['bottom'].set_zorder(1100)
  ax.spines['left'].set_zorder(1100)
  if save:
    # from matplotlib.backends.backend_pgf import FigureCanvasPgf
    # from matplotlib.backend_bases import register_backend
    # register_backend('pdf', FigureCanvasPgf)
    plt.savefig(save, dpi=300)
    # from matplotlib.backends.backend_pgf import FigureCanvasPgf
    # canvas = FigureCanvasPgf(fig)
    # canvas.print_figure('save')
  return



if __name__ == "__main__":
  df = pd.read_csv(table_filename)
  plot_metric_fig(df, 'BSLD', 'BSLD', save='../results/fig_bsl.pdf', bbox_to_anchor=(1, 0.9))
  plot_metric_fig(df, 'AF', 'AF', save='../results/fig_af.pdf', legend=False)
  plot_metric_fig(df, 'BSLD', 'AF', save='../results/fig_bsl_af_nl.pdf', legend=False)
  plot_metric_fig(df, 'AWF', 'AF', save='../results/fig_awf_af_nl.pdf', legend='upper right')
  plot_metric_fig(df, 'AWF', 'AWF', save='../results/fig_awf.pdf')
  plot_metric_fig(df, 'P2SF', 'P2SF', save='../results/fig_p2sf.pdf', legend='upper right', bbox_to_anchor=(1, 0.52))
  # plt.show()
