include () {
    [[ -f "$1" ]] && source "$1"
}

include ~/.bash_aliases

export ANSIBLE_NOCOWS=1

export EDITOR=vim
export VISUAL=vim
export TERM=xterm-256color
export LESS=-r
export TITLEBAR="\e]2;\u@\h \w\a"       
export PATH=$HOME/bin:/usr/local/bin:/sbin:/usr/local/sbin:$PATH

export HISTCONTROL=ignoreboth
export HISTSIZE=100000
export HISTFILESIZE=$HISTSIZE
shopt -s histappend
shopt -s checkwinsize
shopt -s cmdhist
set completion-ignore-case On
# PROMPT_COMMAND="history -a;history -c;history -r;$PROMPT_COMMAND"

export PS1="\n\u@\e[33;1m\h\e[0m \e[34;1m\w\e[0m\n"'\$ '
export GIT_PROMPT_END='\n\$ '
export GIT_PROMPT_ONLY_IN_REPO=1
export GIT_PROMPT_START="\n\u@\e[33;1m\h\e[0m \e[34;1m\w\e[0m"
include ~/.bash-git-prompt/gitprompt.sh

# fuzzy finder
export FZF_DEFAULT_OPTS="-e"
[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# host-specific settings
include .profile_${HOSTNAME%%.*}

[ -e ~/.bashrc ] && . ~/.bashrc
