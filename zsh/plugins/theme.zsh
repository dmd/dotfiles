if [[ $UID -eq 0 ]]; then
    local user_color='red'
    local user_symbol='#'
else
    local user_color='green'
    local user_symbol='❯'
fi

local user_host='%{$terminfo[bold]$fg[$user_color]%}%n@%m %{$reset_color%}'

local current_dir='%{$terminfo[bold]$fg[blue]%}%~ %{$reset_color%}'
local git_branch='$(git_prompt_info)'

PROMPT=$'\n'"${user_host}${current_dir}${git_branch}
%B${user_symbol}%b "

ZSH_THEME_GIT_PROMPT_PREFIX="%{$fg[yellow]%}‹"
ZSH_THEME_GIT_PROMPT_SUFFIX="› %{$reset_color%}"