###############################################################################
# Original code by: William Thompson
# Edited by: Seung-mok Lee 
#            physmlee@gmail.com
#
#  Change output directories to your own directories.
# Find '# SETTING: directory' comments and modify directories.
#
# Usage
#     (pyroot) $ python perform_trim.py 'xtal' 'run' 'subrun' 'multiplicity'
#             xtal: 2, 3, 4, 6 or 7
#             run: every available runs
#             subrun: 0 ~ 999
#             multiplicity: 'single' or 'multi' 
# Example
#     (pyroot) $ python perform_trim.py 2 1544 0 single
#             will trim crystal 2, run 1544, subrun 0, single hit events.
#             Note that you must activate virtual environment containing
#             pyroot.
# 
#  This script trims the MRGD data file. Save single (or multiple) hit 
# scintillation-like events without muon coincidence. Crystal number, run 
# number, subrun number, and multiplicity are to be taken from command line.
#  The vesion of MRGD data production is set to V00-04-19.
#  Tested on python 3.8.10, root 6.24/00 version.
#
# Update logs
#  Changes suited for Olaf server.
#  BDT cut coefficients were modified and ES cut was applied.
#    [ref] https://docdb.wlab.yale.edu/cosine/ShowDocument?docid=914
###############################################################################

# 0. Prepare
# Import packages
import sys
import os
from array import array
# ROOT package was imported after checking file existence
# to  avoid the ROOT importing time consumption.

# Get input from command line.
xtal = int(sys.argv[1])  # First input
run = int(sys.argv[2])  # Second input
subrun = int(sys.argv[3])  # Third input
multiplicity = sys.argv[4]  # Fourth input

# Check bad input
assert xtal in [2, 3, 4, 6, 7]  # Use good crystals only
assert (run >= 1000) and (run <= 9999)
assert (subrun >= 0) and (subrun <= 999)
assert multiplicity in ['single', 'multi']

# 1. Read MRGD data file
# MRGD data path and file name format
file_path_format = '/mnt/lustre/ibs/cupcosine/data/COSINE/MRGD/phys/V00-04-19/{run:d}/'
file_name_format = 'mrgd_M{run:06d}.root.{subrun:03d}'

# Read the data file into TChain
file_path = file_path_format.format(run=run)
file_name = file_name_format.format(run=run, subrun=subrun)
if not os.path.isfile(file_path + file_name):  # If there is no such file wanted, exit.
  print('NoMRGD ', sys.argv, file=sys.stderr)  # Print result
  exit()

# Set output directory and name
home_directory = './../../'  # SETTING: directory
output_path = home_directory + 'data/'
output_path += f'C{xtal}/' if multiplicity == 'single' else f'C{xtal}_multi/'
output_name = f'trim_T{run:06d}_C{xtal}.root.{subrun:03d}'

# If trimmed data larger than 10kB already exists, skip it.
if os.path.isfile(output_path + output_name) and (os.path.getsize(output_path + output_name) > 10000):
  print('AlreadyExist ', sys.argv, file=sys.stderr)  # Print result
  exit()

# Importing ROOT takes a few seconds, so import it after file existence check.
import ROOT

# Define TChain and read the data file.
c = ROOT.TChain('ntp')
c.Add(file_path + file_name)

# Check branch existence
branch_list = ['BLSVeto', 'BMuon', 
               'crystal1', 'crystal2', 'crystal3', 'crystal4', 
               'crystal5', 'crystal6', 'crystal7', 'crystal8']
for branch in branch_list:
  if c.GetBranch(branch) == None:  # a branch is not in the MRGD file.
    print('No' + branch + ' ', sys.argv, file=sys.stderr)
    exit()

# Get total number of events before trimming
nOriginalEntries = c.GetEntries()

# 2. Define cuts for trimming
# LS cut
CoincidenceCut = 'BLSVeto.isCoincident==1 &&'
MuonCut = '(BMuon.totalDeltaT0/1e6>30) &&'

# LS coincidence cut
# apply LS charge correction to runs after 1720
LSChargeCorrection = '' if run <= 1720 else '*((4.6165E-6)*(eventsec-1451606400.0)/3600.0+0.92166)'
if multiplicity == 'single':
  LSThresCut = '(BLSVeto.Charge' + LSChargeCorrection + '/143.8<=80 &&'
elif multiplicity == 'multi':
  LSThresCut_M = '!(BLSVeto.Charge' + LSChargeCorrection + '/143.8<=30 &&'

# Crystal coincidence check and scintillation-like event cut
# BDT cut variable was updated.
if xtal==2:
  SingleCut = '(crystal1.nc<4 && crystal3.nc<4 && crystal4.nc<4 && crystal5.nc<4 && crystal6.nc<4 && crystal7.nc<4 && crystal8.nc<3)) &&'
  bdtCut = "((1.52e-06*TMath::Exp(-107.84*bdt[2]) - 1.94 - 29.288*bdt[2])<crystal2.energy)"
  esVar = "((1 - (crystal2.nx2 - crystal2.nx1))/2)"
  eshCut = "(" + esVar + " > 0.5163 )"
  esdCut = "(" + esVar + " - 0.330*bdt[2] < 0.918 )"
elif xtal==3:
  SingleCut = '(crystal1.nc<4 && crystal2.nc<4 && crystal4.nc<4 && crystal5.nc<4 && crystal6.nc<4 && crystal7.nc<4 && crystal8.nc<3)) &&'
  bdtCut = '((1.50e-07*TMath::Exp(-120.0*bdt[3]) + 0.0 - 20.0*bdt[3])<crystal3.energy)'
  esVar = "((1 - (crystal3.nx2 - crystal3.nx1))/2)"
  eshCut = "(" + esVar + " > 0.5079 )"
  esdCut = "(" + esVar + " - 0.552*bdt[3] < 0.902 )"
elif xtal==4:
  SingleCut = '(crystal2.nc<4 && crystal3.nc<4 && crystal1.nc<4 && crystal5.nc<4 && crystal6.nc<4 && crystal7.nc<4 && crystal8.nc<4)) &&'
  bdtCut = '((1.50e-09*TMath::Exp(-110.0*bdt[4]) + 0.3 - 10.0*bdt[4])<crystal4.energy)'
  esVar = "((1 - (crystal4.nx2 - crystal4.nx1))/2)"
  eshCut = "(" + esVar + " > 0.5245 )"
  esdCut = "(" + esVar + " - 0.358*bdt[4] < 0.944 )"
elif xtal==6:
  SingleCut = '(crystal1.nc<4 && crystal2.nc<4 && crystal3.nc<4 && crystal4.nc<4 && crystal5.nc<4 && crystal7.nc<4 && crystal8.nc<3)) &&'
  bdtCut = '((6.01e-08*TMath::Exp(-120.177*bdt[6]) + 0.8 - 21.615*bdt[6]) <crystal6.energy)'
  esVar = "((1 - (crystal6.nx2 - crystal6.nx1))/2)"
  eshCut = "(" + esVar + " > 0.4877 )"
  esdCut = "(" + esVar + " - 0.687*bdt[6] < 0.906 )"
elif xtal==7:
  SingleCut = '(crystal1.nc<4 && crystal2.nc<4 && crystal3.nc<4 && crystal4.nc<4 && crystal5.nc<4 && crystal6.nc<4 && crystal8.nc<3)) &&'
  bdtCut = '((6.01e-08*TMath::Exp(-120.177*bdt[7]) - 0.24 - 31.615*bdt[7])<crystal7.energy)'
  esVar = "((1 - (crystal7.nx2 - crystal7.nx1))/2)"
  eshCut = "(" + esVar + " > 0.4875 )"
  esdCut = "(" + esVar + " - 0.451*bdt[7] < 0.909 )"
scintCut = bdtCut + "&&" + eshCut + "&&" + esdCut

# Waveform precuts
nchargeCut = f'(crystal{xtal}.rqcn>-1) &&'
ncCut = f'(pmt{xtal}1.nc>0 && pmt{xtal}2.nc>0) &&'
t1Cut = f'(pmt{xtal}1.t1>0 && pmt{xtal}2.t1>0) &&'

# Merge every cuts
if multiplicity == 'single':
  allCuts = CoincidenceCut + MuonCut + LSThresCut   + SingleCut + nchargeCut + ncCut + t1Cut + scintCut
elif multiplicity == 'multi':
  allCuts = CoincidenceCut + MuonCut + LSThresCut_M + SingleCut + nchargeCut + ncCut + t1Cut + scintCut

# 3. Create trimmed output file
# Create output directory and file
# if you encounter permission problem, change the output directory or its permission using chmod.
os.makedirs(output_path, exist_ok=True)
newfile = ROOT.TFile(output_path + output_name, 'RECREATE')

# 4. Write tree into output file
newtree = c.CopyTree(allCuts)
nEntries = newtree.GetEntries()

newfile.Write()

# 5. Include run duration info in file
# Define variables for tree I/O
eventsec = array('q', [0])  # 'q' means signed-long-long-int data type
iEvtSec = array('q', [0])
fEvtSec = array('q', [0])
subrunDuration = array('H', [0])  # 'H' means unsigned-short data type

# Set input branch
c.SetBranchAddress('eventsec', eventsec)

# Set output branch
branch_iEvtSec = newtree.Branch('iEvtSec', iEvtSec, 'iEvtSec/L')
branch_fEvtSec = newtree.Branch('fEvtSec', fEvtSec, 'fEvtSec/L')
branch_subrunDuration = newtree.Branch('subrunDuration', subrunDuration, 'subrunDuration/s')

# Get the start time of the subrun
c.GetEntry(0)
iEvtSec[0] = eventsec[0]

# Get the end time of the subrun
c.GetEntry(nOriginalEntries-1)
fEvtSec[0] = eventsec[0]

# Calculate the subrun duration time
subrunDuration[0] = fEvtSec[0] - iEvtSec[0]

# 6. Write time and close file, print out
# Store the time value into the output tree
for i in range(nOriginalEntries):
  branch_iEvtSec.Fill()
  branch_fEvtSec.Fill()
  branch_subrunDuration.Fill()

# Write it
newtree.Write()
newfile.Close()

# Print the output
output_format = '{filename},{xtal},{run},{subrun},{multiplicity},{nOriginalEntries},{nEntries}'
print(output_format.format(filename=sys.argv[0], 
                           xtal=xtal, run=run, subrun=subrun, multiplicity=multiplicity,
                           nOriginalEntries=nOriginalEntries, nEntries=nEntries))

# END OF CODE