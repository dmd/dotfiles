[[ $UID = 0 ]] && ZSH_DISABLE_COMPFIX=true
HISTFILE=$HOME/.zsh_history

for lib ($HOME/dotfiles/zsh/*.zsh)
    source $lib

autoload -U compaudit compinit
compinit -i -C -D

# lower case can mean upper case, but not vice versa
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

# Automatically quote globs in URL and remote references
__remote_commands=(scp rsync)
autoload -U url-quote-magic
zle -N self-insert url-quote-magic
zstyle -e :urlglobber url-other-schema '[[ $__remote_commands[(i)$words[1]] -le ${#__remote_commands} ]] && reply=("*") || reply=(http https ftp)'

export TZ=America/New_York
export PATH=~/bin:~/.cargo/bin:~/.local/bin:/opt/homebrew/bin:/usr/local/bin:/sbin:/usr/local/sbin:$PATH
export EDITOR=emacs
export VISUAL=$EDITOR
export LESS=-r
export HOMEBREW_AUTO_UPDATE_SECS=86400
export FZF_DEFAULT_OPTS='--reverse --border --exact --height=50%'
export AWS_PAGER=""

bindkey -e 
setopt rmstarsilent

alias -g ...='cd ../..'
alias e="emacs -nw"
alias j=z
alias edges='ssh edges@3e.org'
alias htop='TERM=screen htop'
alias mefi='ssh dev.host tail -20 linkwatcher/today.log'
alias sci='ssh-copy-id'
alias s='sudo zsh'
alias ta='tmux attach'

SHORT_HOST=${HOST/.*/}
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

    __conda_setup="$(/cm/shared/anaconda3/bin/conda shell.zsh hook 2> /dev/null)"
    eval "$__conda_setup"
    unset __conda_setup
    alias dcmodify='singularity_run dcmodify'
    alias dcmdump='singularity_run dcmdump'
    alias storescu='singularity_run storescu'
    alias dcmsend='singularity_run dcmsend'
    alias s='sudo bash'
    PATH=~/myemacs/bin:$PATH
fi

if [ -f /cm/shared/.cluster-name-mickey ]; then
    . ~proto/.bashrc.master
    alias s='sudo bash'
fi

export TERM=xterm-256color
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"
export STARSHIP_CONFIG=$HOME/dotfiles/starship.toml
eval "$(starship init zsh)"