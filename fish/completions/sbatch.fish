function __fish_complete_slurm_sbatch_mail_type
    echo BEGIN
    echo END
    echo FAIL
    echo ALL
end

# sbatch (SLURM)
complete -c sbatch --erase
complete -c sbatch -r
complete -c sbatch -s a -l array -d "job array index values" -x
complete -c sbatch -s A -l account -d "charge job to specified account" -x
complete -c sbatch -l bb -d "burst buffer specifications" -x
complete -c sbatch -l bbf -d "burst buffer specification file" -x
complete -c sbatch -s b -l begin -d "defer job until HH:MM MM/DD/YY" -x
complete -c sbatch -l comment -d "arbitrary comment" -x
complete -c sbatch -l cpu-freq -d "cpu frequency (and governor)" -x
complete -c sbatch -s c -l cpus-per-task -d "number of cpus required per task" -x
complete -c sbatch -s d -l dependency -d "job until condition on jobid is satisfied" -x
complete -c sbatch -l deadline -d "remove the job if no ending possible before this deadline" -x
complete -c sbatch -l delay-boot -d "delay boot for desired node features" -x
complete -c sbatch -s D -l chdir -d "set working directory for batch script" -r
complete -c sbatch -s e -l error -d "file for batch script's standard error" -r
complete -c sbatch -l export -d "specify environment variables to export" -x
complete -c sbatch -l export-file -d "specify environment variables file" -r
complete -c sbatch -l get-user-env -d "load environment from local cluster"
complete -c sbatch -l gid -d "group ID to run job as (user root only)" -x
complete -c sbatch -l gres -d "required generic resources" -x
complete -c sbatch -l gres-flags -d "flags related to GRES management" -x
complete -c sbatch -s H -l hold -d "submit job in held state"
complete -c sbatch -l ignore-pbs -d "Ignore #PBS options in the batch script"
complete -c sbatch -s i -l input -d "file for batch script's standard input" -x
complete -c sbatch -s J -l job-name -d "name of job" -x
complete -c sbatch -s k -l no-kill -d "do not kill job on node failure"
complete -c sbatch -s L -l licenses -d "required license, comma separated" -x
complete -c sbatch -s M -l clusters -d "Comma separated list of clusters to issue commands to" -x
complete -c sbatch -s m -l distribution -d "distribution method for processes to nodes" -a "block cyclic arbitrary"
complete -c sbatch -l mail-type -d "notify on state change" -x -a '(__fish_complete_list , __fish_complete_slurm_sbatch_mail_type)'
complete -c sbatch -l mail-user -d "who to send email notification for job state changes" -x
complete -c sbatch -l mcs-label -d "mcs label if mcs plugin mcs/group is used" -x
complete -c sbatch -s n -l ntasks -d "number of tasks to run" -x
complete -c sbatch -l nice -d "decrease scheduling priority by value"
complete -c sbatch -l no-requeue -d "if set, do not permit the job to be requeued"
complete -c sbatch -l ntasks-per-node -d "number of tasks to invoke on each node" -x
complete -c sbatch -s N -l nodes -d "number of nodes on which to run (N = min[-max])" -x
complete -c sbatch -s o -l output -d "file for batch script's standard output" -r
complete -c sbatch -s O -l overcommit -d "overcommit resources"
complete -c sbatch -s p -l partition -d "partition requested" -x -a "(__fish_complete_slurm_comma_separated partitions)"
complete -c sbatch -l parsable -d "outputs only the jobid and cluster name (if present)"
complete -c sbatch -l power -d "power management options" -x
complete -c sbatch -l priority -d "set the priority of the job to value" -x
complete -c sbatch -l profile -d "enable acct_gather_profile for detailed data" -x
complete -c sbatch -l propagate -d "propagate all [or specific list of] rlimits"
complete -c sbatch -s q -l qos -d "quality of service" -x
complete -c sbatch -s Q -l quiet -d "quiet mode (suppress informational messages)"
complete -c sbatch -l reboot -d "reboot compute nodes before starting job"
complete -c sbatch -l requeue -d "if set, permit the job to be requeued"
complete -c sbatch -s s -l oversubscribe -d "over subscribe resources with other jobs"
complete -c sbatch -s S -l core-spec -d "count of reserved cores" -x
complete -c sbatch -l signal -d "signal when time limit within time seconds" -x
complete -c sbatch -l spread-job -d "spread job across as many nodes as possible"
complete -c sbatch -l switches -d "switches and max time to wait for optimum" -x
complete -c sbatch -l thread-spec -d "count of reserved threads" -x
complete -c sbatch -s t -l time -d "time limit" -x
complete -c sbatch -l time-min -d "minimum time limit (if distinct)" -x
complete -c sbatch -l uid -d "user ID to run job as (user root only)" -x
complete -c sbatch -l use-min-nodes -d "if a range of node counts is given, prefer the smaller count"
complete -c sbatch -s v -l verbose -d "verbose mode (multiple -v's increase verbosity)"
complete -c sbatch -s W -l wait -d "wait for completion of submitted job"
complete -c sbatch -l wckey -d "wckey to run job under" -x
complete -c sbatch -l wrap -d "wrap command string in a sh script and submit" -f
complete -c sbatch -l cluster-constraint -d "a list of cluster constraints" -f
complete -c sbatch -l contiguous -d "demand a contiguous range of nodes"
complete -c sbatch -s C -l constraint -d "specify a list of constraints" -x
complete -c sbatch -s F -l nodefile -d "request a specific list of hosts" -r
complete -c sbatch -l mem -d "minimum amount of real memory" -x
complete -c sbatch -l mincpus -d "minimum number of logical processors (threads) per node" -x
complete -c sbatch -l reservation -d "allocate resources from named reservation" -x
complete -c sbatch -l tmp -d "minimum amount of temporary disk" -x
complete -c sbatch -s w -l nodelist -d "request a specific list of hosts" -x -a "(__fish_complete_slurm_comma_separated nodes)"
complete -c sbatch -s x -l exclude -d "exclude a specific list of hosts" -x -a "(__fish_complete_slurm_comma_separated nodes)"
complete -c sbatch -l exclusive -d "allocate nodes in exclusive mode"
complete -c sbatch -l mem-per-cpu -d "maximum amount of real memory per allocated cpu" -x
complete -c sbatch -s B -l extra-node-info -x
complete -c sbatch -l sockets-per-node -d "number of sockets per node to allocate" -x
complete -c sbatch -l cores-per-socket -d "number of cores per socket to allocate" -x
complete -c sbatch -l threads-per-core -d "number of threads per core to allocate" -x
complete -c sbatch -l ntasks-per-core -d "number of tasks to invoke on each core" -x
complete -c sbatch -l ntasks-per-socket -d "number of tasks to invoke on each socket" -x
complete -c sbatch -l cpus-per-gpu -d "number of CPUs required per allocated GPU" -x
complete -c sbatch -s G -l gpus -d "count of GPUs required for the job" -x
complete -c sbatch -l gpu-bind -d "task to gpu binding options" -x
complete -c sbatch -l gpu-freq -d "frequency and voltage of GPUs" -x
complete -c sbatch -l gpus-per-node -d "number of GPUs required per allocated node" -x
complete -c sbatch -l gpus-per-socket -d "number of GPUs required per allocated socket" -x
complete -c sbatch -l gpus-per-task -d "number of GPUs required per spawned task" -x
complete -c sbatch -l mem-per-gpu -d "real memory required per allocated GPU" -x
complete -c sbatch -s h -l help -d "show the help message"
complete -c sbatch -l usage -d "display brief usage message"
complete -c sbatch -s V -l version -d "output version information and exit"

