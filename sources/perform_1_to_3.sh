#!/bin/bash
#SBATCH -J DQC_end_to_end
#SBATCH --partition jepyc
#SBATCH --time 200:00:00
#SBATCH --output %x-%A.out
#SBATCH --error %x-%A.err

cd "$SLURM_SUBMIT_DIR" || exit
cd "./4.TrimmingData/" || exit
TRIM_ID=$(sbatch --parsable submit_trim_singlehit.sh)
echo "Trimming Data Submition: $TRIM_ID"

cd "../5.ExtractRate/" || exit
EXTR_ID=$(sbatch --parsable --dependency=afterok:"$TRIM_ID" submit_graph_rate_vs_time.sh)
echo "Extract Rate Submition: $EXTR_ID"

cd "../6.DrawPlots/" || exit
DRAW_ID=$(sbatch --parsable --dependency=afterok:"$EXTR_ID" submit_draw.sh)
echo "Draw Plots Submition: $DRAW_ID"
