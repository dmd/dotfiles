[[ $UID = 0 ]] && ZSH_DISABLE_COMPFIX=true
HISTFILE=$HOME/.zsh_history
HIST_STAMPS="yyyy-mm-dd"

ZSH_CACHE_DIR="$ZSH/cache"
export ZSHLIB=$HOME/dotfiles/zsh
for lib ($ZSHLIB/lib/*.zsh $ZSHLIB/plugins/*.zsh)
    source $lib

# lower case can mean upper case, but not vice versa
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

# Automatically quote globs in URL and remote references
__remote_commands=(scp rsync)
autoload -U url-quote-magic
zle -N self-insert url-quote-magic
zstyle -e :urlglobber url-other-schema '[[ $__remote_commands[(i)$words[1]] -le ${#__remote_commands} ]] && reply=("*") || reply=(http https ftp)'

export TZ=America/New_York
export PATH=~/bin:~/.local/bin:~/emacslib/bin:/opt/homebrew/bin:/usr/local/bin:/sbin:/usr/local/sbin:$PATH
export ANSIBLE_NOCOWS=1
export EDITOR=emacs
export VISUAL=$EDITOR
export LESS=-r
export HOMEBREW_AUTO_UPDATE_SECS=86400
export FZF_DEFAULT_OPTS='--reverse --border --exact --height=50%'

bindkey -e 
# unsetopt auto_menu
setopt rmstarsilent
setopt HIST_IGNORE_SPACE

alias e="emacs -nw"
alias j=z
alias edges='ssh edges@3e.org'
alias htop='TERM=screen htop'
alias vi='vim'
alias mefi='ssh dev.host tail -20 linkwatcher/today.log'
alias sci='ssh-copy-id'
alias irc='ssh -t dev.host weechat'
alias dh='dirs -v'
alias gca='git commit -v -a'
alias gcam='git commit -a -m'
alias s='sudo zsh'
alias ta='tmux attach'

# per-host customizations
if [[ $SHORT_HOST == dev ]]; then
    alias irc='rm $HOME/.weechat/weechat.log;weechat'
fi

if [[ $SHORT_HOST == ogawa ]]; then
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    alias tun='ssh -D 7890 -f -C -q -N dmd@dev.host'
    alias m='ssh micc'
    alias x='ssh x5backup'
    alias n='ssh root@nisaba'
fi

if [[ $SHORT_HOST == atto || $SHORT_HOST == dromedary ]]; then
    alias tt='tmuxinator tun'
    alias m='ttssh ddrucker@micc.mclean.harvard.edu'
    alias n='ttssh root@nisaba.mclean.harvard.edu'
    alias x='ttssh root@x5backup.mclean.harvard.edu'
    alias o='ttssh ddrucker@ogawa.mclean.harvard.edu'
    alias ogawa=o
    alias pluto='ttssh ddrucker@pluto.mclean.harvard.edu'
fi

micchosts=(micc node1 node2 node3 node4 node5)
if (( ${micchosts[(I)$SHORT_HOST]} )); then
    . ~proto/.bashrc.master

    __conda_setup="$(/cm/shared/anaconda3/bin/conda shell.zsh hook 2> /dev/null)"
    eval "$__conda_setup"
    unset __conda_setup
    alias car='conda activate rapidtide'
    alias dclogs='pushd /home/ddrucker/mictools/miccpipe; docker-compose logs --timestamps -f --tail=10; popd'
    alias dcmodify='singularity run  -B /data -B /home /cm/shared/singularity/images/dcm.sif dcmodify'
    alias dcmdump='singularity run -B /data -B /home /cm/shared/singularity/images/dcm.sif dcmdump'
    alias storescu='singularity run -B /data -B /home /cm/shared/singularity/images/dcm.sif storescu'
    alias dcmsend='singularity run -B /data -B /home /cm/shared/singularity/images/dcm.sif dcmsend'
    alias s='sudo bash'
    newfmri() {
        singularity build fmriprep-${1}.simg docker://poldracklab/fmriprep:${1}
    }
fi

if [[ "$TERM" != dumb ]]; then
    export TERM=xterm-256color
    test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"
    alias sz=it2dl
    alias rz=it2ul
    export LC_ALL=en_US.UTF-8  # tmux needs this
    export STARSHIP_CONFIG=$HOME/dotfiles/starship.toml
    eval "$(starship init zsh)"
else
    export PS1=$
fi
