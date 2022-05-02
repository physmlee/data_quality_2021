#!/bin/bash
#SBATCH -J perform_trim_single
#SBATCH --array=0-999
#SBATCH --partition jepyc
#SBATCH --time 99:00:00
#SBATCH --output out/%x.csv
#SBATCH --error out/%x.err
#SBATCH --open-mode append

# lines above are sbatch submission setting
# job name is 'perform_trim_single'
# arrayjob index from 0 to 999. The index can be used via $SLURM_ARRAY_TASK_ID, and it will be used for subrun number.
# use jepyc node
# time wall is set to 99 hours. 
# output (error) messages will be saved in out/perform_trim_single.csv (.err) file

subrun=$SLURM_ARRAY_TASK_ID

cd "$SLURM_SUBMIT_DIR" || exit

run=$1
for xtal in {2,3,4,6,7}
do
  python perform_trim.py "$xtal" "$run" "$subrun" single
done
