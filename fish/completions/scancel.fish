function __fish_complete_slurm_list_job_states_scancel
    printf "PENDING\tJob is awaiting resource allocation.\n"
    printf "RUNNING\tJob currently has an allocation.\n"
    printf "SUSPENDED\tJob has an allocation, but execution has been suspended.\n"
end

# scancel (SLURM)
complete -c scancel --erase
__fish_complete_slurm_common scancel
complete -c scancel --no-files
complete -c scancel -a "(__fish_complete_slurm_comma_separated job_ids)"
complete -c scancel -s b -l batch -d "signal batch shell for specified job"
complete -c scancel -s f -l full -d "signal batch shell and all steps for specified job"
complete -c scancel -s H -l hurry -d "avoid burst buffer stage out"
complete -c scancel -s i -l interactive -d "require response from user for each job"
complete -c scancel -s M -l clusters -d "clusters to issue commands to"
complete -c scancel -s Q -l quiet -d "disable warnings"
complete -c scancel -l sibling -d "remove an active sibling job from a federated job"
complete -c scancel -s s -l signal -d "signal to send to job, default is SIGKILL"
complete -c scancel -s t -l state -d "act only on jobs in this state" -x -a "(__fish_complete_slurm_list_job_states_scancel)"
complete -c scancel -l wckey -d "act only on jobs with this workload charactization key"
