#!/bin/bash
# ---------------------------------------------------------------------
# SLURM script for job resubmission on a Compute Canada cluster. 
# ---------------------------------------------------------------------
#SBATCH --account=def-pbellec
#SBATCH --cpus-per-task=8
#SBATCH --time=00:45:00
#SBATCH --mem=4G
#SBATCH --mail-user=francois.nadeau.1@umontreal.ca
#SBATCH --mail-type=ALL
#SBATCH --output=%pwd/cimaq_2021_scans_%j.tar.xz
# ---------------------------------------------------------------------
echo "Current working directory: `pwd`"
echo "Starting run at: `date`"
# ---------------------------------------------------------------------

module load python/3.8
python3.8 get_scan_archive.py
