# Load colors if the colors function is available
if type "colors" &>/dev/null; then
    colors
fi
export LSCOLORS="Gxfxcxdxbxegedabagacad"

if [[ "$OSTYPE" =~ (darwin|freebsd).* ]]; then
  ls -G . &>/dev/null && alias ls='ls -G'
  [[ -n "$LS_COLORS" || -f "$HOME/.dircolors" ]] && gls --color -d . &>/dev/null && alias ls='gls --color=tty'
else
  if [[ -z "$LS_COLORS" ]]; then
    command -v dircolors >/dev/null && eval "$(dircolors -b)"
  fi

  ls --color -d . &>/dev/null && alias ls='ls --color=tty' || { ls -G . &>/dev/null && alias ls='ls -G'; }

  # No direct bash equivalent for zsh's zstyle
  # Consider using a utility like 'grc' (Generic Colouriser) as an alternative
fi

if command diff --color . . &>/dev/null; then
  alias diff='diff --color'
fi
