###############################################################################
# Original code by: William Thompson
# Edited by: Seung-mok Lee 
#            physmlee@gmail.com
#
# This script loops over trimmed files, recording the number of events after
# cuts in each file. Output is saved as a TGraph and as a text file.
#
#  Change output directories to your own directories.
# Find '# SETTING: directory' comments and modify directories.
#
# Usage
#     (pyroot) $ python graph_rate_vs_time.py 'xtal'
#             xtal: 2, 3, 4, 6 or 7
# Example
#     (pyroot) $ python graph_rate_vs_time.py  2
#             will record the number of single hit events of crystal 2.
#
# Update logs
#  Changes suited for Olaf server.
###############################################################################

# 0. Prepare
# import packages
import sys
import os
import math
import ROOT

# set root, make TCanvas and TGraphErrors instances
ROOT.gROOT.SetBatch(1)
canvas = ROOT.TCanvas('c','c',1000,600)
graph = ROOT.TGraphErrors()

xtal = sys.argv[1]  # first parameter

# 1. Prepare for reading data file
# set directory
home_directory = './../../'  # SETTING: directory
trimmed_path = home_directory + 'data/C{}/'.format(xtal)
output_path = home_directory + 'graphs/'

# create output directory
# if you encounter permission problem, change the output directory or its permission using chmod.
os.makedirs(output_path, exist_ok=True)

# 2. Read data and write event rate into csv file
# create output csv (.csv) file
with open(output_path + 'RawRateTime_xtal{0}.csv'.format(xtal), 'w') as outfile:
  # for each trimmed data files,
  filenamelist = sorted(os.listdir(trimmed_path))
  filenum = len(filenamelist)
  for filename in filenamelist:
    # get run/subrun info
    run = int(filename[8:12])
    subrun = int(filename[-3:])
    
    # if file smaller than 10kB, it is probably empty or processed incorrectly, so skip
    if os.path.getsize(trimmed_path + filename) > 10000:
      data_file = ROOT.TFile(trimmed_path + filename)  # read file
      tree = data_file.Get('ntp')  # read tree
      nTotal_events = tree.Draw('crystal{0}.energy'.format(xtal), 'crystal{0}.energy >= 1 && crystal{0}.energy <= 6'.format(xtal), 'gOff')  # count event number in 1~6 keV
      
      # evaluate event rate (=event number / subrun duration)
      tree.GetEntry(0)
      try:
        pct_of_full_subrun = tree.subrunDuration / 7200
        event_rate = nTotal_events / pct_of_full_subrun
        event_rate_err = math.sqrt(nTotal_events) / pct_of_full_subrun
      except ZeroDivisionError:
        event_rate = 0
        event_rate_err = 0
      mid_time = tree.iEvtSec + tree.subrunDuration/2.

      # plot the point into TGraph instance
      graph.SetPoint(graph.GetN(), mid_time, event_rate)
      graph.SetPointError(graph.GetN()-1, 0, event_rate_err)

      # write the data into csv (.csv) file
      print(run, subrun, mid_time, event_rate, event_rate_err, file=outfile, sep=',')

      # close the trimmed data file
      data_file.Close()

# 3. Write TGraph into root file
# create output root file to write TGraph instance
out_graph_file = ROOT.TFile(output_path + 'RateTime_xtal{0}.root'.format(xtal), 'recreate')

# write
graph.SetName('graph')
#canvas.Draw()  # use this line if you want to see the graph immediately.
graph.Write()
out_graph_file.Close()

# END OF CODE