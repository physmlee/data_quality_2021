#!/bin/bash
#SBATCH -J C4div
#SBATCH --partition jepyc
#SBATCH --time 200:00:00
#SBATCH --output %x.out
#SBATCH --error %x.err
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-user=physmlee@gmail.com

cd "$SLURM_SUBMIT_DIR" || exit

python draw_rate_hist_div.py 1476972372 1492740372
python draw_rate_hist_div.py 1492740372 1508508372
python draw_rate_hist_div.py 1508508372 1524276372
python draw_rate_hist_div.py 1524276372 1540044372
python draw_rate_hist_div.py 1540044372 1555812372
python draw_rate_hist_div.py 1555812372 1571580372
python draw_rate_hist_div.py 1571580372 1587348372
python draw_rate_hist_div.py 1587348372 1603116372
python draw_rate_hist_div.py 1603116372 1624927832
