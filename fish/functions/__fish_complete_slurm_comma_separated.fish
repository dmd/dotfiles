function __fish_slurm_list_accounts
    sacctmgr --parsable --noheader list Account | cut -d "|" -f 1
end

function __fish_slurm_list_job_ids
    # jobs
    squeue --noheader --array --user (whoami) --format="%i|%j %T %r" | string replace -r '\|' '\t' | string replace ' None' ''
    # array jobs
    squeue --noheader --array --user (whoami) --format="%F|%j %T %r" | string replace -r '\|' '\t' | string replace ' None' ''
end

function __fish_slurm_list_job_names
    squeue --noheader --user (whoami) --format="%j|%A %u" | string replace -r '\|' '\t'
end

function __fish_slurm_list_nodes
    sinfo --noheader --Node --format '%N|%P' --noheader | string replace -r '\|' '\t'
end

function __fish_slurm_list_partitions
    sinfo --noheader --format '%P|%N' --noheader | string replace -r '\|' '\t'
end

function __fish_slurm_list_users
    squeue --noheader --format="%u"
end

function __fish_complete_slurm_comma_separated -d "comma-separated list of objects" --argument-names entity prefix
    switch $entity
        case "accounts"
            __fish_complete_list , __fish_slurm_list_accounts $prefix
        case "job_ids"
            __fish_complete_list , __fish_slurm_list_job_ids $prefix
        case "job_names"
            __fish_complete_list , __fish_slurm_list_job_names $prefix
        case "nodes"
            __fish_complete_list , __fish_slurm_list_nodes $prefix
        case "partitions"
            __fish_complete_list , __fish_slurm_list_partitions $prefix
        case "users"
            __fish_complete_list , __fish_slurm_list_users $prefix
    end
end
