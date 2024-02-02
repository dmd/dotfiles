if [ -d /cm/shared ]; then
    . ~proto/.bashrc.master
    if [ -f /cm/shared/.cluster-name-micc ]; then
        PATH=~/myemacs/bin:$PATH
    fi
fi
exec fish -l
