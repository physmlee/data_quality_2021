#!/bin/bash
#SBATCH -J perform_draw_rate_time
#SBATCH --array=2,3,4,6,7
#SBATCH --partition jepyc
#SBATCH --time 99:00:00
#SBATCH --output out/%x_%a.out
#SBATCH --error out/%x_%a.err
#SBATCH --open-mode append

xtal=$SLURM_ARRAY_TASK_ID

cd "$SLURM_SUBMIT_DIR" || exit

python draw_rate_vs_time.py "$xtal"
