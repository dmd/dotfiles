function __fish_complete_slurm_scontrol_update_needs_joblist
    # Figure out if the current invocation already has a job.
    if not __fish_seen_subcommand_from update
      return 1
    end
    if __fish_complete_slurm_scontrol_has_jobid
      return 1
    end
    set -l cmd (commandline -opc)
    if set -q cmd[3]
      echo $cmd[3]
      return 1
    end
    return 0
end

function __fish_complete_slurm_scontrol_update_needs_spec
    # Figure out if the current invocation already has a job.
    if not __fish_seen_subcommand_from update
      return 1
    end
    if __fish_complete_slurm_scontrol_update_needs_joblist
      return 1
    end
    return 0
end

function __fish_complete_slurm_scontrol_has_jobid
    # find JobID=...
    set -l cmd (commandline -opc)
    for j in $cmd
      if string match -q -r -i '^JobID=[0-9]+(_[0-9]+)?$' -- $j
        echo $j
        return 0
      end
    end
    return 1
end

function __fish_complete_slurm_scontrol_jobspec_for_job
    set -l jobid (__fish_complete_slurm_scontrol_has_jobid)
    if set -q jobid
      # get existing settings
      scontrol --oneliner show $jobid | \
        string replace -ra ' ' '\n' | \
        string replace -a '(null)' '' | \
        string replace -a 'CPUs/Task' 'CPUsPerTask' | \
        string match -re 'ArrayTaskThrottle|CPUsPerTask|Dependency|Gres|NumCPUs|NodeList|Mem'
    end
    echo "ArrayTaskThrottle=
Dependency=after:
Dependency=afterany:
Dependency=afternotok:
Dependency=afterok:
Dependency=singleton"
end

# scontrol (SLURM)
complete -c scontrol --erase
complete -c scontrol --no-files
complete -c scontrol -s a -l all -d "Equivalent to 'all' command"
complete -c scontrol -s d -l details -d "Equivalent to 'details' command"
complete -c scontrol -s -federation -d "Report federated job information if a member of one"
complete -c scontrol -s F -l future -d "Report information about nodes in 'FUTURE' state"
complete -c scontrol -l hide -d "Do not display hidden partitions"
complete -c scontrol -l local -d "Report information only about jobs on the local cluster"
complete -c scontrol -s M -l cluster -d "Cluster to issue commands to"
complete -c scontrol -s o -l oneliner -d "Report output one record per line"
complete -c scontrol -s Q -l quiet -d "Print no messages other than error messages"
complete -c scontrol -l sibling -d "Report information about all sibling jobs on a federated cluster"
complete -c scontrol -s u -l d -d "Update job as user 'uid' instead of the invoking user"
complete -c scontrol -s h -l help -d "show help"
complete -c scontrol -s v -l verbose -d "verbosity level"
complete -c scontrol -s V -l version -d "output version information and exit"

complete -c scontrol -n __fish_use_subcommand -a hold -d "prevent specified job from starting"
complete -c scontrol -n __fish_use_subcommand -a release -d "permit specified job to start (see hold)"
complete -c scontrol -n __fish_use_subcommand -a top -d "Put specified job first in queue for user"
complete -c scontrol -n __fish_use_subcommand -a show -d "display state of identified entity"
complete -c scontrol -n __fish_use_subcommand -a update -d "update job, node, partition, reservation, or step"

complete -c scontrol -n "__fish_seen_subcommand_from hold top" -x -a "(__fish_complete_slurm_comma_separated job_ids)"
complete -c scontrol -n "__fish_seen_subcommand_from release" -x -a "(__fish_complete_slurm_comma_separated job_ids | grep Held)"

complete -c scontrol -n "__fish_seen_subcommand_from show" -a "(__fish_complete_slurm_comma_separated job_ids JobId=)"

complete -c scontrol -n "__fish_complete_slurm_scontrol_update_needs_joblist" -a "(__fish_complete_slurm_comma_separated job_ids JobId=)"
complete -c scontrol -n "__fish_complete_slurm_scontrol_has_jobid" -x -a "(__fish_complete_slurm_scontrol_jobspec_for_job)"
complete -c scontrol -n "false; and __fish_complete_slurm_scontrol_update_needs_spec" -x -a "
     Account=
     AdminComment=
     ArrayTaskThrottle=
     BurstBuffer=
     Clusters=
     ClusterFeatures=
     Comment=
     Contiguous=
     CoreSpec=
     CPUsPerTask=
     Deadline=
     DelayBoot=
     Dependency=after:
     Dependency=afterany:
     Dependency=afternotok:
     Dependency=afterok:
     Dependency=singleton
     EligibleTime=
     EndTime
     ExcNodeList=
     Features=
     Gres=
     JobId=
     Licenses=
     MinCPUsNode=
     MinMemoryCPU=
     MinMemoryNode=
     MinTmpDiskNode=
     TimeMin=
     JobName=
     Name=
     Nice=
     NodeList=
     NumCPUs=
     NumNodes=
     NumTasks=
     OverSubscribe=
     Partition=
     Priority=
     QOS=
     Reboot=
     ReqCores=
     ReqNodeList=
     ReqNodes=
     ReqProcs=
     ReqSockets=
     ReqThreads=
     Requeue=
     ReservationName=
     ResetAccrueTime
     SiteFactor=
     StdOut=
     Shared=
     StartTime=
     Switches=
     wait-for-switch=
     TasksPerNode=
     ThreadSpec=
     TimeLimit=
     UserID=
     WCKey=
     WorkDir=
"
