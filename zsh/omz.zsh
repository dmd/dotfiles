######### my own omz
ZSH_CACHE_DIR="$ZSH/cache"
autoload -U compaudit compinit

# Figure out the SHORT hostname
if [[ "$OSTYPE" = darwin* ]]; then
  # macOS's $HOST changes with dhcp, etc. Use ComputerName if possible.
  SHORT_HOST=$(scutil --get ComputerName 2>/dev/null) || SHORT_HOST=${HOST/.*/}
else
  SHORT_HOST=${HOST/.*/}
fi

ZSH_COMPDUMP="${HOME}/.zcompdump-${SHORT_HOST}-${ZSH_VERSION}"

# Construct zcompdump OMZ metadata
zcompdump_revision="#omz revision: $(builtin cd -q "$ZSH"; git rev-parse HEAD 2>/dev/null)"
zcompdump_fpath="#omz fpath: $fpath"

# Delete the zcompdump file if OMZ zcompdump metadata changed
if ! command grep -q -Fx "$zcompdump_revision" "$ZSH_COMPDUMP" 2>/dev/null \
   || ! command grep -q -Fx "$zcompdump_fpath" "$ZSH_COMPDUMP" 2>/dev/null; then
  command rm -f "$ZSH_COMPDUMP"
  zcompdump_refresh=1
fi

if [[ $ZSH_DISABLE_COMPFIX != true ]]; then
    source $ZSH/lib/compfix.zsh
    handle_completion_insecurities
    compinit -i -C -d "${ZSH_COMPDUMP}"
else
    compinit -u -C -d "${ZSH_COMPDUMP}"
fi

# Append zcompdump metadata if missing
if (( $zcompdump_refresh )); then
  # Use `tee` in case the $ZSH_COMPDUMP filename is invalid, to silence the error
  # See https://github.com/ohmyzsh/ohmyzsh/commit/dd1a7269#commitcomment-39003489
  tee -a "$ZSH_COMPDUMP" &>/dev/null <<EOF

$zcompdump_revision
$zcompdump_fpath
EOF
fi

unset zcompdump_revision zcompdump_fpath zcompdump_refresh

