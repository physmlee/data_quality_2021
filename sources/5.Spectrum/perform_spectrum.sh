#!/bin/bash
#SBATCH -J DQCspec
#SBATCH --array=2,3,4,6,7
#SBATCH --partition jepyc
#SBATCH --time 99:00:00
#SBATCH --output out/%x_%a.out
#SBATCH --error out/%x_%a.err
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-user=smlee.olaf@gmail.com

xtal=$SLURM_ARRAY_TASK_ID
cd "$SLURM_SUBMIT_DIR" || exit
python spectrum.py "$xtal"
