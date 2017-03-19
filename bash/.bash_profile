include () {
    [[ -f "$1" ]] && source "$1"
}

include ~/.bash_aliases

export TERM=xterm-256color
export LESS=-r
export TITLEBAR="\e]2;\u@\h \w\a"       
export PS1="\n\u@\e[33;1m\h\e[0m \e[34;1m\w\e[0m\n"'\$ '
export GIT_PROMPT_ONLY_IN_REPO=1
export PATH=$HOME/bin:/usr/local/bin:/usr/local/sbin:$PATH:/sbin

export HISTCONTROL=ignoredups:erasedups
export HISTSIZE=10000
shopt -s histappend
shopt -s checkwinsize
shopt -s cmdhist
set completion-ignore-case On


include ~/.bash-git-prompt/gitprompt.sh

# host-specific settings
include .profile_${HOSTNAME%%.*}
[[ -f ~/.abinitiorc ]] && source ~/.profile_abinitio
