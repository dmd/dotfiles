[[ $UID = 0 ]] && ZSH_DISABLE_COMPFIX=true

export ZSH="$HOME/.oh-my-zsh"
ZSH_CUSTOM=$HOME/dotfiles/zshcustom
ZSH_THEME="dmd"
plugins=(git z fzf docker)
source $ZSH/oh-my-zsh.sh

HIST_STAMPS="yyyy-mm-dd"
SAVEHIST=100000
export TZ=America/New_York
export PATH=~/bin:~/.local/bin:/usr/local/bin:/sbin:/usr/local/sbin:$PATH
export ANSIBLE_NOCOWS=1
export EDITOR=vim
export VISUAL=$EDITOR
export TERM=xterm-256color
export LESS=-r

bindkey -e 

alias j=z
alias edges='ssh edges@3e.org'
alias htop='TERM=screen htop'
alias vi='vim'  # not sure if needed
alias mefi='ssh dev.host tail -20 linkwatcher/today.log'
alias sci='ssh-copy-id'
alias irc='ssh -t dev.host weechat'
alias dh='dirs -v'

## finally, per-host customizations
if [[ $HOST == dev ]]; then
    alias irc='rm $HOME/.weechat/weechat.log;weechat'
fi

if [[ $HOST == ogawa.mclean.harvard.edu ]]; then
    alias tun='ssh -D 7890 -f -C -q -N dmd@dev.host'
    alias m='ssh micc'
    alias x='ssh x5backup'
fi

if [[ $HOST == pico.local ]]; then
    alias books="rsync -rtv dev.host:/var/lib/transmission-daemon/downloads/ ~/Desktop/tmp/books/"
    . /usr/local/miniconda3/etc/profile.d/conda.sh
fi

micchosts=(micc node1 node2 node3 node4 node5)
if (( ${micchosts[(I)$HOST]} )); then
    alias q='qstat -u "*"'
    . ~proto/.bashrc.master
    export PATH=/cm/local/apps/docker/current/bin/:/cm/local/apps/docker-compose/1.17.1/bin/:/cm/shared/anaconda3/bin:${FSLDIR}/bin:/cm/shared/ICA-AROMA:${PATH}
fi

