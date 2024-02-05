function _fetch_slurm_job_info
    /cm/shared/apps/slurm/current/bin/squeue | awk 'NR>1 {printf "%s\t%s (%s)\n", $1, $3, $4}'
end