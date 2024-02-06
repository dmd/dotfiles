function _fetch_slurm_job_info_users
    /cm/shared/apps/slurm/current/bin/squeue --noheader  -o "%u" | sort -u
end
