#!/bin/bash
#SBATCH -J perform_graph_rate_time
#SBATCH --array=2,3,4,6,7
#SBATCH --partition jepyc
#SBATCH --time 99:00:00
#SBATCH --output out/%x_%A.out
#SBATCH --error out/%x_%A.err
#SBATCH --open-mode append

xtal=$SLURM_ARRAY_TASK_ID

cd "$SLURM_SUBMIT_DIR" || exit

python graph_rate_vs_time.py "$xtal"
