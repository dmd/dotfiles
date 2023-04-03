for lib in $HOME/dotfiles/bash/*.bash; do 
    source $lib
done 
[[ -r "/opt/homebrew/etc/profile.d/bash_completion.sh" ]] && . "/opt/homebrew/etc/profile.d/bash_completion.sh"

HISTSIZE=-1
HISTFILESIZE=-1

export TZ=America/New_York
export PATH=~/bin:~/.cargo/bin:~/.local/bin:/opt/homebrew/bin:/usr/local/bin:/sbin:/usr/local/sbin:$PATH
export EDITOR=emacs
export VISUAL=$EDITOR
export LESS=-r
export HOMEBREW_AUTO_UPDATE_SECS=86400
export FZF_DEFAULT_OPTS='--reverse --border --exact --height=50%'
export AWS_PAGER=""

set -o emacs 

alias e="emacs -nw"
alias j=z
alias edges='ssh edges@3e.org'
alias htop='TERM=screen htop'
alias vi='vim'
alias mefi='ssh dev.host tail -20 linkwatcher/today.log'
alias sci='ssh-copy-id'
alias s='sudo bash'
alias ta='tmux attach'

SHORT_HOST=$(hostname)
SHORT_HOST=${SHORT_HOST%%.*}
# per-host customizations
case $SHORT_HOST in
    dev)
        alias irc='rm $HOME/.weechat/weechat.log;weechat'
        ;;

    ogawa)
        export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
        alias m='ssh micc'
        alias x='ssh root@x5backup'
        alias n='ssh root@nisaba'
        complete -C '/usr/local/bin/aws_completer' aws
#        export LC_ALL=en_US.UTF-7  # tmux needs this
        ;;

    atto|dromedary|ddrucker-mba)
        alias m='ssh ddrucker@micc.mclean.harvard.edu'
        alias n='ssh root@nisaba.mclean.harvard.edu'
        alias x='ssh root@x5backup.mclean.harvard.edu'
        alias o='ssh ddrucker@ogawa.mclean.harvard.edu'
        alias pluto='ssh ddrucker@pluto.mclean.harvard.edu'
        ;;
esac

function singularity_run() {
    singularity run -B /data -B /home -B /n /cm/shared/singularity/images/dcm.sif "$1"
}

if [ -f /cm/shared/.cluster-name-micc ]; then
    . ~proto/.bashrc.master

    __conda_setup="$(/cm/shared/anaconda3/bin/conda shell.bash hook 2> /dev/null)"
    eval "$__conda_setup"
    unset __conda_setup
    alias dcmodify='singularity_run dcmodify'
    alias dcmdump='singularity_run dcmdump'
    alias storescu='singularity_run storescu'
    alias dcmsend='singularity_run dcmsend'
    PATH=~/myemacs/bin:$PATH
fi

if [ -f /cm/shared/.cluster-name-mickey ]; then
    . ~proto/.bashrc.master
fi

[ -f ~/.fzf.bash ] && source ~/.fzf.bash
export TERM=xterm-256color
test -e "${HOME}/.iterm2_shell_integration.bash" && source "${HOME}/.iterm2_shell_integration.bash"
export STARSHIP_CONFIG=$HOME/dotfiles/starship.toml
eval "$(starship init bash)"
