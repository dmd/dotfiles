export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="agnoster"
ZSH_THEME="bira"

COMPLETION_WAITING_DOTS="true"
HIST_STAMPS="yyyy-mm-dd"
SAVEHIST=100000

plugins=(git z)

source $ZSH/oh-my-zsh.sh

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

## finally, per-host customizations
if [[ $HOST == dev ]]; then
    alias irc='rm $HOME/.weechat/weechat.log;weechat'
fi

if [[ $HOST == ogawa.mclean.harvard.edu ]]; then
    alias tun='ssh -D 7890 -f -C -q -N dmd@dev.host'
    alias m='ssh micc'
    alias x='ssh x5backup'
fi

if [[ $HOST == pico ]]; then
    alias books="rsync -rtv dev.host:/var/lib/transmission-daemon/downloads/ ~/Desktop/tmp/books/"
fi

