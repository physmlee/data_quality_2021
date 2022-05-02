#!/bin/bash
#SBATCH -J C2stb
#SBATCH --partition jepyc
#SBATCH --time 200:00:00
#SBATCH --output %x.out
#SBATCH --error %x.err
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-user=smlee.olaf@gmail.com

cd "$SLURM_SUBMIT_DIR" || exit

python draw_rate_hist_stb.py
