function __fish_complete_slurm_common -d "common completions for slurm commands" --argument-names cmd
    complete -c $cmd -s A -l account -d "account or list of accounts" -x -a "(__fish_complete_slurm_comma_separated accounts)"
    complete -c $cmd -s n -l name -d "job name or list of job names" -x -a "(__fish_complete_slurm_comma_separated job_names)"
    complete -c $cmd -s u -l user -d "user or list of users" -x -a "(__fish_complete_slurm_comma_separated users)"

    complete -c $cmd -x -s w -l nodelist -d "node or list of nodes"
    complete -c $cmd -x -s p -l partition -d "partition or list of partitions"
    complete -c $cmd -x -s q -l qos -d "qos or list of qos's"
    complete -c $cmd -x -s R -l reservation -d "reservation"
    complete -c $cmd -l help -d "show help"
    complete -c $cmd -s v -l verbose -d "verbosity level"
    complete -c $cmd -s V -l version -d "output version information and exit"
end
