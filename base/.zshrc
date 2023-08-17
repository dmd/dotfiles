bindkey -e 
setopt rmstarsilent

####
#### completion
####

[[ $UID = 0 ]] && ZSH_DISABLE_COMPFIX=true

zmodload -i zsh/complist
WORDCHARS=''

unsetopt menu_complete   # do not autoselect the first completion entry
unsetopt flowcontrol
setopt auto_menu         # show completion menu on successive tab press
setopt complete_in_word
setopt always_to_end

zstyle ':completion:*:*:*:*:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|=*' 'l:|=* r:|=*'
zstyle ':completion:*' special-dirs true
zstyle ':completion:*' list-colors ''
zstyle '*' single-ignored show

autoload -U +X bashcompinit && bashcompinit
autoload -U compaudit compinit
compinit -i -C -D

# lower case can mean upper case, but not vice versa
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'


####
#### history
####

HISTFILE=$HOME/.zsh_history
HISTSIZE=10000000
SAVEHIST=10000000

setopt BANG_HIST                 # Treat the '!' character specially during expansion.
setopt EXTENDED_HISTORY          # Write the history file in the ":start:elapsed;command" format.
setopt INC_APPEND_HISTORY        # Write to the history file immediately, not when the shell exits.
setopt SHARE_HISTORY             # Share history between all sessions.
setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicate entries first when trimming history.
setopt HIST_IGNORE_DUPS          # Don't record an entry that was just recorded again.
setopt HIST_IGNORE_ALL_DUPS      # Delete old recorded entry if new entry is a duplicate.
setopt HIST_FIND_NO_DUPS         # Do not display a line previously found.
setopt HIST_IGNORE_SPACE         # Don't record an entry starting with a space.
setopt HIST_SAVE_NO_DUPS         # Don't write duplicate entries in the history file.
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks before recording entry.
setopt HIST_VERIFY               # Don't execute immediately upon history expansion.
setopt HIST_BEEP                 # Beep when accessing nonexistent history.

####
#### color (supports linux and macos)
####

autoload -U colors && colors

if [[ "$OSTYPE" == darwin* ]]; then
  alias ls='ls -G'
else
  alias ls='ls --color=tty'
fi

if command diff --color . . &>/dev/null; then
  alias diff='diff --color'
fi

source $HOME/dotfiles/zsh/fzf.zsh    # fuzzy finder
source $HOME/dotfiles/zsh/z.zsh      # 31d1's z navigator

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

    atto|dromedary|ddrucker-mba|ogawa)
        alias m='ssh ddrucker@micc.mclean.harvard.edu'
        alias n='ssh root@nisaba.mclean.harvard.edu'
        alias x='ssh root@x5backup.mclean.harvard.edu'
        alias o='ssh ddrucker@ogawa.mclean.harvard.edu'
        alias pluto='ssh ddrucker@pluto.mclean.harvard.edu'
        ;;
esac

function dcm_run() {
    singularity run -B /data -B /home -B /n /cm/shared/singularity/images/dcm.sif "$1"
}

if [ -f /cm/shared/.cluster-name-micc ]; then
    . ~proto/.bashrc.master

    __conda_setup="$(/cm/shared/anaconda3/bin/conda shell.zsh hook 2> /dev/null)"
    eval "$__conda_setup"
    unset __conda_setup
    alias dcmodify='dcm_run dcmodify'
    alias dcmdump='dcm_run dcmdump'
    alias storescu='dcm_run storescu'
    alias dcmsend='dcm_run dcmsend'
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
