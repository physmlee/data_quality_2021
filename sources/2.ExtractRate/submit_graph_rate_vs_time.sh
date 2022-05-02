#!/bin/bash
#SBATCH -J submit_graph_rate_time
#SBATCH --partition jepyc
#SBATCH --time 200:00:00
#SBATCH --output %x_%A.out
#SBATCH --error %x_%A.err

cd "$SLURM_SUBMIT_DIR" || exit
mkdir -p "$SLURM_SUBMIT_DIR/out/"

extr_job_id_file="$SLURM_SUBMIT_DIR/out/extr_job_id.txt"
[ -e "$extr_job_id_file" ] && rm "$extr_job_id_file"  # remove if file exists

trim_job_list_file="../4.TrimmingData/out/trim_job_list.txt"
read -r trim_job_list < $trim_job_list_file  # read trim job ids

# submit rate extracting job with dependency on the trimming data jobs
JOB_ID=$(sbatch --parsable --dependency=afterok"$trim_job_list" perform_graph_rate_vs_time.sh)
printf ":%s" "$JOB_ID" >> "$extr_job_id_file"  # save job id
