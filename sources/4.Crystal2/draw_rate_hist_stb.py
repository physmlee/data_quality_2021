###############################################################################
# Written by: Seung-mok Lee 
#             physmlee@gmail.com
#
# This script draws the distribution of number of events in each sub-run from
# the file output by graph_rate_vs_time.py, except for long instable period
# specified in 'unstables' list. (find comment # NOTE: unstable periods)
# Various exclusion levels / criteria are applied to idenfity bad sub-runs.
# This script is for crystal 2.
#
#  Change output directories to your own directories.
# Find '# SETTING: directory' comments and modify directories.
#
# Usage
#     (pyroot) $ python draw_rate_hist_stb.py
###############################################################################

# 0. Prepare
# import packages
import ROOT
import sys
import csv
import statistics as stats
import math
from scipy.stats import poisson
from array import array
import sqlite3
import os

# set Root
ROOT.gStyle.SetOptStat(0)


# define calculators
# calculate where is the desired cl
def calc_exclusion(mu, desired_cl):
  cl = 0
  k = 0
  while cl < desired_cl:
    cl += poisson.pmf(k, mu)
    k += 1
  return k-1


# calculate number of entries at which Chauvenet's criterion will set cutoff
def calc_chauvenet(nSubruns, mu):
  k = int(mu)
  while True:
    expected_counts = poisson.pmf(k, mu) * nSubruns
    if expected_counts <= 0.5:
      break
    else:
      k+=1
  return k


# define printer
# prints excluded subruns to stdout. Also writes to outfilename if provided
def print_excluded_subruns(xtal, cutoff, conversion_factor_subrun, filename, outfilename=''):
  with open(filename) as infile:
    csv_data = csv.reader(infile, delimiter=',')
    excluded_runs = []
    excluded_subruns = []
    if outfilename != '':
      outfile = open(outfilename, 'w')
    for row in csv_data:
      if float(row[3])*conversion_factor_subrun >= cutoff:
        output = str(row[0]) + '.' + str(row[1]).zfill(3) + ': ' + str(float(row[3])*conversion_factor_subrun)
        print(output)
        if outfilename != '':
          outfile.write(output + '\n')  
        excluded_runs.append(row[0])
        excluded_subruns.append(row[1])
    if outfilename != '':
      outfile.close()
  
  return excluded_runs, excluded_subruns


def print_excluded_subruns_period(xtal, cutoff, conversion_factor_subrun, filename, time_start, time_end, outfilename=''):
  with open(filename) as infile:
    csv_data = csv.reader(infile, delimiter=',')
    excluded_runs = []
    excluded_subruns = []
    if outfilename != '':
      outfile = open(outfilename, 'w')
    for row in csv_data:
      if float(row[3])*conversion_factor_subrun >= cutoff and float(row[2]) >= time_start and float(row[2]) <= time_end:
        output = str(row[0]) + '.' + str(row[1]).zfill(3) + ': ' + str(float(row[3])*conversion_factor_subrun)
        print(output)
        if outfilename != '':
          outfile.write(output + '\n')  
        excluded_runs.append(row[0])
        excluded_subruns.append(row[1])
    if outfilename != '':
      outfile.close()
  
  return excluded_runs, excluded_subruns


def print_excluded_subruns_stable(xtal, cutoff, conversion_factor_subrun, filename, unstables, outfilename=''):
  with open(filename) as infile:
    csv_data = csv.reader(infile, delimiter=',')
    excluded_runs = []
    excluded_subruns = []
    if outfilename != '':
      outfile = open(outfilename, 'w')
    for row in csv_data:
      time = float(row[2])
      unstable = False
      for time_start, time_end in unstables:
        unstable = unstable or (time >= time_start and time <= time_end)
      if float(row[3])*conversion_factor_subrun >= cutoff or unstable:
        output = str(row[0]) + '.' + str(row[1]).zfill(3) + ': ' + str(float(row[3])*conversion_factor_subrun)
        print(output)
        if outfilename != '':
          outfile.write(output + '\n')  
        excluded_runs.append(row[0])
        excluded_subruns.append(row[1])
    if outfilename != '':
      outfile.close()
  
  return excluded_runs, excluded_subruns


# define color painter
# color good subruns as blue and bad subruns as red
# criteria is cutoff
# return the colored graph
def color_code_graph(filename, cutoff):
  infile = ROOT.TFile(filename)
  g_in = infile.Get('graph')
  
  x_good = []
  y_good = []
  y_good_err = []
  x_bad = []
  y_bad = []
  y_bad_err = []
  
  x_graph = g_in.GetX()
  y_graph = g_in.GetY()
  for i in range(g_in.GetN()):
    # Subtracting 788918400 to account for time offset
    #if y_graph[i] < cutoff:
    if y_graph[i] < cutoff:
      x_good.append(x_graph[i]-788918400)
      y_good.append(y_graph[i])
      y_good_err.append(g_in.GetErrorY(i))
    else:
      x_bad.append(x_graph[i]-788918400)
      y_bad.append(y_graph[i])
      y_bad_err.append(g_in.GetErrorY(i))
  
  x_good_arr = array('d', x_good)
  y_good_arr = array('d', y_good)
  x_good_err_arr = array('d', [0]*len(x_good))
  y_good_err_arr = array('d', y_good_err)
  x_bad_arr = array('d', x_bad)
  y_bad_arr = array('d', y_bad)
  x_bad_err_arr = array('d', [0]*len(x_bad))
  y_bad_err_arr = array('d', y_bad_err)
  g_good = ROOT.TGraphErrors( len(x_good), x_good_arr, y_good_arr,
                x_good_err_arr, y_good_err_arr )
  g_bad = ROOT.TGraphErrors( len(x_bad), x_bad_arr, y_bad_arr,
                x_bad_err_arr, y_bad_err_arr )
  
  g_good.SetMarkerColor(ROOT.kBlue)
  g_bad.SetMarkerColor(ROOT.kRed)
  g_good.SetLineColor(ROOT.kBlue)
  g_bad.SetLineColor(ROOT.kRed)
  g_total = ROOT.TMultiGraph()
  g_total.Add(g_good, 'p*')
  g_total.Add(g_bad, 'p*')
  
  x_i = x_graph[0] - 788918400
  x_f = x_graph[-1] - 788918400
  
  return g_total, (x_i, x_f)


def color_code_graph_stable(filename, cutoff, unstables):
  infile = ROOT.TFile(filename)
  g_in = infile.Get('graph')
  
  x_good = []
  y_good = []
  y_good_err = []
  x_bad = []
  y_bad = []
  y_bad_err = []
  
  x_graph = g_in.GetX()
  y_graph = g_in.GetY()
  for i in range(g_in.GetN()):
    # Subtracting 788918400 to account for time offset
    time = x_graph[i]
    unstable = False
    for time_start, time_end in unstables:
      unstable = unstable or (time >= time_start and time <= time_end)
    
    if y_graph[i] < cutoff and not unstable:
      x_good.append(x_graph[i]-788918400)
      y_good.append(y_graph[i])
      y_good_err.append(g_in.GetErrorY(i))
    else:
      x_bad.append(x_graph[i]-788918400)
      y_bad.append(y_graph[i])
      y_bad_err.append(g_in.GetErrorY(i))
  
  x_good_arr = array('d', x_good)
  y_good_arr = array('d', y_good)
  x_good_err_arr = array('d', [0]*len(x_good))
  y_good_err_arr = array('d', y_good_err)
  x_bad_arr = array('d', x_bad)
  y_bad_arr = array('d', y_bad)
  x_bad_err_arr = array('d', [0]*len(x_bad))
  y_bad_err_arr = array('d', y_bad_err)
  g_good = ROOT.TGraphErrors( len(x_good), x_good_arr, y_good_arr,
                x_good_err_arr, y_good_err_arr )
  g_bad = ROOT.TGraphErrors( len(x_bad), x_bad_arr, y_bad_arr,
                x_bad_err_arr, y_bad_err_arr )
  
  g_good.SetMarkerColor(ROOT.kBlue)
  g_bad.SetMarkerColor(ROOT.kRed)
  g_good.SetLineColor(ROOT.kBlue)
  g_bad.SetLineColor(ROOT.kRed)
  g_total = ROOT.TMultiGraph()
  g_total.Add(g_good, 'p*')
  g_total.Add(g_bad, 'p*')
  
  x_i = x_graph[0] - 788918400
  x_f = x_graph[-1] - 788918400
  
  return g_total, (x_i, x_f)


# define sqlite database writer functions
# !deprecated
def create_connection(db_file):
  """
  create a database connection to the SQLite database
  specified by the db_file
  :param db_file: database file
  :return: Connection object or None
  """
  conn = None
  try:
    conn = sqlite3.connect(db_file)
  except Exception as e:
    print(e)
  
  return conn


# !deprecated
def update_subrun(conn, xtal, task1, task2):
  """
  update priority, begin_date, and end date of a task
  :param conn:
  :param xtal:
  :param task1:
  :param task2:
  :return: None
  """
  sql = f''' UPDATE set3_catalog
        SET C{xtal} = ?
        WHERE runnum == ? AND subrunnum == ?'''
  cur = conn.cursor()
  cur.execute(sql, task1)
  sql = ''' UPDATE set3_catalog
        SET anabit = ?
        WHERE runnum == ? AND subrunnum == ? AND anabit == 1'''
  cur.execute(sql, task2)
  conn.commit()


# Main starts here!
# 1. Prepare in main function
xtal = 2  # first parameter
unstables = [
  (1587218412.0, 1589731377.0)
]  # NOTE: unstable periods

conversion_factor_subrun = 1  # Number is in counts

# set canvas and histogram
canvas = ROOT.TCanvas('c','c',800,600)
hist_min = 0
hist_maxes = [0, 0, 60, 60, 60, 200, 60, 60, 200]
hist = ROOT.TH1D('h','',hist_maxes[xtal]-hist_min, hist_min, hist_maxes[xtal])

# 2. Read .csv Data File
# file path & name
home_directory = './../../'  # SETTING: directory
filepath = home_directory + 'graphs/'
filename = filepath + f'RawRateTime_xtal{xtal}.csv'

# read file
with open(filename) as infile:
  csv_data = csv.reader(infile, delimiter=',')
  rates = []
  times = []
  for row in csv_data:
    time = float(row[2])
    rate = float(row[3])
    
    unstable = False
    for time_start, time_end in unstables:
      unstable = unstable or (time >= time_start and time <= time_end)
    
    if rate != 0 and not unstable:
      _=hist.Fill(rate * conversion_factor_subrun)
      rates.append(rate * conversion_factor_subrun)
      times.append(time)

# 3. Analysis; Fit with Poissonian Function
median = stats.median(rates)

fxn_min = 0
peak_location = hist.GetXaxis().GetBinCenter(hist.GetMaximumBin())
# Set fxn fit range max to ~5 std above mean
fxn_max = peak_location + 5*math.sqrt(peak_location)  # Don't fit outliers
fxn = ROOT.TF1('pois', '[0]*TMath::Poisson(x, [1])')
fxn.SetParameters(12000, median)
fxn.SetParName(0, 'Normalization')
fxn.SetParName(1, '#mu')
hist.Fit(fxn, '', '', fxn_min, fxn_max)

# 4. Plot CLs
nEntries = fxn.GetParameter(0)
mu = fxn.GetParameter(1)
sigma = math.sqrt(mu)

# determine rate cutoff for 1-sided confidence level
# plus 1 is to be on more conservative side of discrete exclusion
sig_3 = 0.99865
sig_4 = 0.999968
sig_5 = 1-0.000000573303144
cutoff_3_sig = calc_exclusion(mu, sig_3) + 1
cutoff_99 = calc_exclusion(mu, 0.999) + 1
cutoff_4_sig = calc_exclusion(mu, sig_4) + 1
cutoff_5_sig = calc_exclusion(mu, sig_5) + 1

cutoff_chauvenet = calc_chauvenet(nEntries, mu)

# 5. Draw Everything
hist.Draw()
fxn.Draw('same')

canvas.SetLogy(1)

hist.GetXaxis().SetTitle('Counts per sub-run')
hist.SetTitle('Crystal {0} (1-6 keV)'.format(xtal))
hist.SetLineWidth(2)

mu_line = ROOT.TLine(mu, 0., mu, hist.GetMaximum())
mu_line.SetLineColor(ROOT.kGreen)
mu_line.SetLineWidth(2)
mu_line.Draw()

sigma_3_line = ROOT.TLine(cutoff_3_sig, 0., cutoff_3_sig, hist.GetMaximum())
line_99 = ROOT.TLine(cutoff_99, 0., cutoff_99, hist.GetMaximum())
sigma_4_line = ROOT.TLine(cutoff_4_sig, 0., cutoff_4_sig, hist.GetMaximum())
sigma_5_line = ROOT.TLine(cutoff_5_sig, 0., cutoff_5_sig, hist.GetMaximum())
chauvenet_line = ROOT.TLine(cutoff_chauvenet, 0., cutoff_chauvenet, hist.GetMaximum())

sigma_3_line.SetLineColor(ROOT.kRed)
sigma_3_line.SetLineWidth(2)
line_99.SetLineColor(ROOT.kBlue)
line_99.SetLineWidth(2)
sigma_4_line.SetLineColor(ROOT.kRed)
sigma_4_line.SetLineWidth(2)
sigma_5_line.SetLineColor(ROOT.kRed)
sigma_5_line.SetLineWidth(2)
chauvenet_line.SetLineColor(ROOT.kMagenta)
chauvenet_line.SetLineWidth(2)

sigma_3_line.Draw('same')
line_99.Draw('same')
sigma_4_line.Draw('same')
sigma_5_line.Draw('same')
chauvenet_line.Draw('same')

leg = ROOT.TLegend(0.6,0.65,0.9,0.9)
leg.AddEntry(mu_line, 'Mean', 'l')
leg.AddEntry(sigma_3_line, '3, 4, 5#sigma', 'l')
leg.AddEntry(line_99, '99.9% CL', 'l')
leg.AddEntry(chauvenet_line, 'Chauvenet Threshold', 'l')
leg.Draw('same')

canvas.Update()
print(f'The count cutoff at 99.9% CL is {cutoff_99} counts')
print(f'The Chauvenet count cutoff is {cutoff_chauvenet} counts')

#canvas.Draw();input('Waiting')  # use this line if you want to see the graph immediately.

# save plot
plot_path = home_directory + 'plots/'
os.makedirs(plot_path, exist_ok=True)
hist_plot_name = f'StableRateHist_xtal{xtal}.pdf'
canvas.SaveAs(plot_path + hist_plot_name)

# 6. Exclude Bad Subruns & Print the Result
result_path = home_directory + 'result/'
os.makedirs(result_path, exist_ok=True)

# Print out sub-runs whose rates exceed given CLs
outfile_99 = result_path + f'stb_bad_subruns_999pct_xtal{xtal}.txt'
outfile_chauvenet = result_path + f'stb_bad_subruns_chauvenet_xtal{xtal}.txt'

print('The following sub-runs exceed 3-sigma')
print_excluded_subruns_stable(xtal, cutoff_3_sig, conversion_factor_subrun, filename, unstables)
print('The following sub-runs exceed 99.9% CL')
excluded_runs, excluded_subruns = print_excluded_subruns_stable(xtal, cutoff_99, conversion_factor_subrun, filename, unstables, outfile_99)
print('The following sub-runs exceed 4-sigma')
print_excluded_subruns_stable(xtal, cutoff_4_sig, conversion_factor_subrun, filename, unstables)
print('The following sub-runs exceed 5-sigma')
print_excluded_subruns_stable(xtal, cutoff_5_sig, conversion_factor_subrun, filename, unstables)
print('The following sub-runs excluded by Chauvenet\'s criterion')
print_excluded_subruns_stable(xtal, cutoff_chauvenet, conversion_factor_subrun, filename, unstables, outfile_chauvenet)

# 7. Draw Colored Subruns vs Time Graph
# Draw graph with excluded sub-runs in red
colored_graph, (t_min, t_max) = color_code_graph(home_directory + f'graphs/RateTime_xtal{xtal}.root', cutoff_99)
time_canvas = ROOT.TCanvas('c_t', 'c_t', 1600, 600)
colored_graph.Draw('a')

colored_graph.GetXaxis().SetRangeUser(t_min-1000000, t_max+1000000)
colored_graph.GetYaxis().SetRangeUser(0, cutoff_99 * 2)
colored_graph.GetXaxis().SetTimeDisplay(1)
time_canvas.Draw()
colored_graph.GetXaxis().SetTimeFormat("%Y-%m")
colored_graph.GetXaxis().SetTitle('Date [yyyy-mm]')
colored_graph.GetYaxis().SetTitle('Counts')
colored_graph.SetTitle(f'Crystal {xtal} Rate vs. Time')

time_canvas.Update()

#time_canvas.Draw();input('Waiting')  # use this line if you want to see the graph immediately.

# save plot
time_plot_name = f'StbColoredRateHist_xtal{xtal}.pdf'
time_canvas.SaveAs(plot_path + time_plot_name)

# END
