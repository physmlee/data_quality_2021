#!/bin/bash
#SBATCH -J submit_draw
#SBATCH --partition jepyc
#SBATCH --time 200:00:00
#SBATCH --output %x_%a.out
#SBATCH --error %x_%a.err

cd "$SLURM_SUBMIT_DIR" || exit
mkdir -p "$SLURM_SUBMIT_DIR/out/"

extr_job_id_file="../5.ExtractRate/out/extr_job_id.txt"
read -r extr_job_list < $extr_job_id_file  # read extract job id

# submit draw job with dependency on the extract rate job
sbatch --dependency=afterok"$extr_job_list" perform_draw_rate_vs_time.sh
sbatch --dependency=afterok"$extr_job_list" perform_draw_rate_hist.sh
