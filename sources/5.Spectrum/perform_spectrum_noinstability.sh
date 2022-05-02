#!/bin/bash
#SBATCH -J DQCspecNoI
#SBATCH --array=2,7
#SBATCH --partition jepyc
#SBATCH --time 99:00:00
#SBATCH --output out/%x_%a.out
#SBATCH --error out/%x_%a.err
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-user=smlee.olaf@gmail.com

xtal=$SLURM_ARRAY_TASK_ID
cd "$SLURM_SUBMIT_DIR" || exit
python spectrum_noinstability.py "$xtal"
