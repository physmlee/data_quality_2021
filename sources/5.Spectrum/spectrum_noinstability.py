###############################################################################
# Written by: Seung-mok Lee 
#             physmlee@gmail.com
#
# This script loops over trimmed files, stacks spectrum from good/bad sub-runs,
# and draw them together.
# Here, we use the bad sub-runs listed in the 
# '(main)/BadCandidates/noinstability_xtal#.txt' file, which is the bad 
# sub-run list outside of the long term instability.
# As a result, you will be able to compare spectrums from good / bad sub-runs
# without long term instabile period.
# You must run 'spectrum.py' code before run this code, to generate the 
# spectrum for good sub-runs.
# 
# Your bad sub-run list file should fowwlow the following format
# ####.@@@: ~~~~~~
# where #### is the run number and @@@ is the sub-run number.
# 
# Example
# 1544.122: 24.0
# 1544.123: 24.0
# 
#  Change output directories to your own directories.
#  Change final result directory & file name for you.
# Find '# SETTING: directory' comments and modify directories.
#
# Usage
#     (pyroot) $ python spectrum_noinstability.py 'xtal'
#             xtal: 2 or 7
# Example
#     (pyroot) $ python spectrum_noinstability.py  2
#             will draw the spectrum of crystal 2.
###############################################################################

# 0. Prepare
# import packages
import os
import sys
import ROOT

# set root, make TCanvas and spectrum (TH1D) instances
ROOT.gROOT.SetBatch(1)
xtal = sys.argv[1]  # first parameter

canvas = ROOT.TCanvas('c', 'c', 1000, 600)
spectrum_min = 1.  # keV
spectrum_max = 6.  # keV
spectrum_bin_size = 0.25  # keV
spectrum_bad = ROOT.TH1D('bad_no_instability', f'Crystal {xtal} Spectrum (Normed)', int((spectrum_max - spectrum_min) /
                         spectrum_bin_size), spectrum_min, spectrum_max)
spectrum_this = "this({nbins},{min},{max})".format(nbins=int((spectrum_max - spectrum_min) /
                          spectrum_bin_size), min=spectrum_min, max=spectrum_max)

# 1. Prepare for reading data file
# set directory
home_directory = './../../'  # SETTING: directory
trimmed_path = home_directory + 'data/C{}/'.format(xtal)
output_path = home_directory + 'spectrum/'

# Read bad sub-run list
# SETTING: final result
bad_sub_path = home_directory + 'BadCandidates/'
bad_sub_name = 'noinstability_xtal{}.txt'.format(xtal)
bad_sub_file = open(bad_sub_path + bad_sub_name, "r")

# the tuple (run, sub-run) of bad sub-runs are in list 'bad_subs'
bad_subs = []
for line in bad_sub_file:
  run = line[0:4]
  sub = line[5:8]
  bad_subs.append((run, sub))

# Read existing spectrum
spectrum_file_name = 'Spectrum_xtal{}.root'.format(xtal)
spectrum_file = ROOT.TFile(output_path + spectrum_file_name)
spectrum_good = spectrum_file.Get('good')

# 2. Read data and stack histogram
filenamelist = sorted(os.listdir(trimmed_path))
filenum = len(filenamelist)
for fileidx, filename in enumerate(filenamelist):
  print(fileidx, ' / ', filenum)
  
  # if file smaller than 10kB, it is probably empty or processed incorrectly, so skip
  if os.path.getsize(trimmed_path + filename) <= 10000:
    continue
  
  # select spectrum to write
  run = filename[8:12]
  sub = filename[-3:]
  
  if (run, sub) not in bad_subs:
    continue
  
  # open the data file
  data_file = ROOT.TFile(trimmed_path + filename)  # read file
  tree = data_file.Get('ntp')  # read tree
  
  try:
    tree.Draw('crystal{0}.energy>>'.format(xtal) + spectrum_this, 'crystal{0}.energy >= 1 && crystal{0}.energy <= 6'.format(xtal), 'gOff')
    this = ROOT.gDirectory.Get("this")
    spectrum_bad.Add(this)
  except:
    print('histogram error for {run}.{sub}'.format(run=run, sub=sub))
  
  # close
  data_file.Close()

# 3. Draw spectrums and save
good_max = spectrum_good.GetMaximum()
good_sumw = spectrum_good.GetSumOfWeights()
good_height = good_max / good_sumw
bad_max = spectrum_bad.GetMaximum()
bad_sumw = spectrum_bad.GetSumOfWeights()
try:
  bad_height = bad_max / bad_sumw
except:
  bad_height = 0
height = max(good_height, bad_height) * 1.05

spectrum_good.Scale(1 / good_sumw)
try:
  spectrum_bad.Scale(1 / bad_sumw)
except:
  _=None

spectrum_good.GetXaxis().SetRangeUser(spectrum_min, spectrum_max)
spectrum_bad.GetXaxis().SetRangeUser(spectrum_min, spectrum_max)
spectrum_good.GetYaxis().SetRangeUser(0, height)
spectrum_bad.GetYaxis().SetRangeUser(0, height)
spectrum_good.GetXaxis().SetTitle('Energy [keV]')
spectrum_good.GetYaxis().SetTitle('Counts')

print(good_height, bad_height, height)

spectrum_good.SetLineWidth(2)
spectrum_good.SetStats(0)
spectrum_good.Draw("hist")

spectrum_bad.SetLineColor(ROOT.kRed)
spectrum_bad.SetLineWidth(1)
spectrum_bad.SetStats(0)
spectrum_bad.Draw("E1SAME")

legend = ROOT.TLegend(0.6, 0.7, 0.83, 0.9)
legend.AddEntry(spectrum_good, "Good Sub-runs", "l")
legend.AddEntry(spectrum_bad, "Bad Sub-runs out of Instability", "l")
legend.Draw()

canvas.SetTitle(f'Crystal {xtal} Spectrum (Normed)')
canvas.Update()

# create output directory
# if you encounter permission problem, change the output directory or its permission using chmod.
os.makedirs(output_path, exist_ok=True)
canvas.SaveAs(output_path + 'Spectrum_no_instability_xtal{0}.pdf'.format(xtal))

# create output root file
out_root_file = ROOT.TFile(output_path + 'Spectrum_no_instability_xtal{0}.root'.format(xtal), 'recreate')

# write
spectrum_good.SetName('good')
spectrum_good.Write()

spectrum_bad.SetName('bad_no_instability')
spectrum_bad.Write()

out_root_file.Close()

# END
