[[ $UID = 0 ]] && ZSH_DISABLE_COMPFIX=true

export ZSH="$HOME/.oh-my-zsh"
ZSH_CUSTOM=$HOME/dotfiles/zshcustom
ZSH_THEME="dmd"
plugins=(z fzf docker)
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
unsetopt auto_menu

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

# per-host customizations
if [[ $SHORT_HOST == dev ]]; then
    alias irc='rm $HOME/.weechat/weechat.log;weechat'
fi

if [[ $SHORT_HOST == ogawa ]]; then
    alias tun='ssh -D 7890 -f -C -q -N dmd@dev.host'
    alias m='ssh micc'
    alias x='ssh x5backup'
fi

if [[ $SHORT_HOST == pico ]]; then
    alias books="rsync -rtv dev.host:/var/lib/transmission-daemon/downloads/ ~/Desktop/tmp/books/"
    . /usr/local/miniconda3/etc/profile.d/conda.sh
fi

micchosts=(micc node1 node2 node3 node4 node5)
if (( ${micchosts[(I)$SHORT_HOST]} )); then
    . ~proto/.bashrc.master

    __conda_setup="$(/cm/shared/anaconda3/bin/conda shell.zsh hook 2> /dev/null)"
    eval "$__conda_setup"
    unset __conda_setup
fi
