#!/bin/bash
#SBATCH -p short
#SBATCH -J nextflow_O2
#SBATCH -t 0-12:00
#SBATCH --mem=1G
#SBATCH --mail-type=END

SAMPLEDIR=$1
SAMPLEID=$(basename $SAMPLEDIR)

module purge
module load java

/n/groups/lsp/mcmicro/tools/o2/config_pre_reg.sh -s -u $SAMPLEDIR > $SAMPLEDIR/memory.config

nextflow run labsyspharm/mcmicro -profile O2,WSI,GPU --in $SAMPLEDIR -w /n/scratch/users/${USER:0:1}/$USER/work -c $(dirname "$SAMPLEDIR")/base.config -c $SAMPLEDIR/memory.config -publish_dir_mode link
