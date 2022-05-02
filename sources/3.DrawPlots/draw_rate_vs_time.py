###############################################################################
# Original code by: William Thompson
# Edited by: Seung-mok Lee 
#            physmlee@gmail.com
#
# This helper script draws a preexisting TGraph with a human-readable x-axis.
# Can draw graph in counts or dru (or other units).
#
#  Change output directories to your own directories.
# Find '# SETTING: directory' comments and modify directories.
#
# Usage
#     (pyroot) $ python draw_rate_vs_time.py 'xtal'
#             xtal: 2, 3, 4, 6 or 7
# Example
#     (pyroot) $ python draw_rate_vs_time.py  2
#             will draw the event rate vs time graph of crystal 2.
#
# Update logs
#  Changes suited for Olaf server.
###############################################################################

# 0. Prepare
# import packages
import ROOT
import sys
import os

xtal = int(sys.argv[1])  # first parameter

mass = [-1000000, 8.26, 9.15, 9.16, 18.01, 18.28, 12.5, 12.5, 18.28]  # crystal mass
keV_window_width = 5.  # how many keV rate was integrated over

# create output directory
# if you encounter permission problem, change the output directory or its permission using chmod.
home_directory = './../../'  # SETTING: directory
plot_path = home_directory + 'plots/'
os.makedirs(plot_path, exist_ok=True)

# make TCanvas
canvas = ROOT.TCanvas('c','c',1600,600)

# 1. Read data
infile = ROOT.TFile.Open(home_directory + f'graphs/RateTime_xtal{xtal}.root')
in_graph = infile.graph

nPoints = in_graph.GetN()  # number of graph points

# 2. Convert rate to dru
# convert number of events in 2 hours to dru
conversion_factor = 12/mass[xtal]/keV_window_width

graph = ROOT.TGraphErrors()
for i in range(nPoints):  # for each points,
  if ROOT.TMath.AreEqualRel(0.0, in_graph.GetX()[i], 1e-6):
    pass
  else:
    # convert to ROOT time. ROOT time starts Jan 1, 1995
    # and convert rate to dru
    graph.SetPoint(graph.GetN(), in_graph.GetX()[i]-788940000, in_graph.GetY()[i] * conversion_factor)
    graph.SetPointError(graph.GetN()-1, 0, in_graph.GetEY()[i] * conversion_factor)

# 3. Set graph format
graph.Draw('AP')
graph.GetXaxis().SetRangeUser(graph.GetX()[0]-1000000, graph.GetX()[graph.GetN()-1]+1000000)
canvas.SetLogy(1)
graph.GetXaxis().SetTimeDisplay(1)
graph.GetXaxis().SetTimeFormat("%Y-%m")
graph.GetXaxis().SetTitle('Date [yyyy-mm]')
graph.GetYaxis().SetTitle('Rate [dru (counts/keV/kg/day)]')
graph.SetTitle(f'Crystal {xtal} Rate vs. Time')

# 4. Show and save
#canvas.Draw();input('Waiting')  # use this line if you want to see the graph immediately.
canvas.SaveAs(plot_path + f'RawRateTime_xtal{xtal}.pdf')

# END OF CODE