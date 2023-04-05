autoload -U colors && colors
export LSCOLORS="Gxfxcxdxbxegedabagacad"

if [[ "$OSTYPE" == (darwin|freebsd)* ]]; then
  ls -G . &>/dev/null && alias ls='ls -G'
  [[ -n "$LS_COLORS" || -f "$HOME/.dircolors" ]] && gls --color -d . &>/dev/null && alias ls='gls --color=tty'
else
  if [[ -z "$LS_COLORS" ]]; then
    (( $+commands[dircolors] )) && eval "$(dircolors -b)"
  fi

  ls --color -d . &>/dev/null && alias ls='ls --color=tty' || { ls -G . &>/dev/null && alias ls='ls -G' }

  zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
fi

if command diff --color . . &>/dev/null; then
  alias diff='diff --color'
fi

