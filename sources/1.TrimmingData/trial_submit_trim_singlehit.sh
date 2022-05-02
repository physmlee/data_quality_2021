#!/bin/bash
#SBATCH -J trial_submit_trim_single
#SBATCH --partition jepyc
#SBATCH --time 120:00:00
#SBATCH --output %x-%A.out
#SBATCH --error %x-%A.err

# lines above are sbatch submission setting
# job name is 'trial_submit_trim_single'
# use jepyc node
# time wall is set to 120 hours. 
# output (error) messages will be saved in trial_submit_trim_single-######.out (.err) file
#######################################################################################


# submit perform_trim jobs to slurm.
# only two run numbers (1555, 1625) will be trimmed.
maxjobs=20

# function to check how many jobs are running for me in jepyc node.
function summary() {
  squeue "$@" | awk '
  BEGIN {
    abbrev["R"]="(Running)"
    abbrev["PD"]="(Pending)"
    abbrev["CG"]="(Completing)"
    abbrev["F"]="(Failed)"
  }
  NR>1 {a[$5]++}
  NR>1 {sum++}
  END {
    printf "%d", sum
  }'
}

# make output directory
cd "$SLURM_SUBMIT_DIR" || exit
mkdir -p "$SLURM_SUBMIT_DIR/out/"
trim_job_list_file="$SLURM_SUBMIT_DIR/out/trim_job_list.txt"
[ -e "$trim_job_list_file" ] && rm "$trim_job_list_file"  # remove if file exists

# in trial version, trim data for only two following runs. 
for run in 1555 1625
do
  while [ "$(summary -u "$USER")" -gt $maxjobs ]  # check job number I am running
  do
    sleep 10
  done  # exit if the node is not possessed by me.
  
  # trim one run. submit the perform_trim job to slurm.
  JOB_ID=$(sbatch --parsable perform_trim_singlehit_onerun.sh "$run")
  while [ "$JOB_ID" == "" ]  # if sbatch submission fails,
  do
    sleep 10
    JOB_ID=$(sbatch --parsable perform_trim_singlehit_onerun.sh "$run")  # try again
  done
  
  echo "trimming run $run at job $JOB_ID"
  printf ":%s" "$JOB_ID" >> "$trim_job_list_file"  # save job ids
done
