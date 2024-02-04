# Cluster-specific configuration
if test -d /cm/shared
    function dcm_run
        singularity run -B /data -B /home -B /n /cm/shared/singularity/images/dcm.sif $argv
    end
    abbr dcmodify 'dcm_run dcmodify'
    abbr dcmdump 'dcm_run dcmdump'
    abbr storescu 'dcm_run storescu'
    abbr dcmsend 'dcm_run dcmsend'
    abbr s 'sudo bash'

    if test -f /cm/shared/.cluster-name-mickey
       alias q 'squeue -o "%.10i %.9u %.10j %.8T %.6C %12N %.10M %.20l"'
       alias qu 'squeue -u $USER -o "%.10i %.9u %.10j %.8T %.6C %12N %.10M %.20l"'
       alias slacct 'sacct --format JobName%15,JobID,TimelimitRaw,TotalCPU,MaxRSS,MaxVMSize,MaxPages,Elapsed,State,Nodelist --units=G'
       eval /cm/shared/anaconda3/bin/conda "shell.fish" "hook" $argv | source
    else
       alias q 'qstat -u "*"'
    end
end
