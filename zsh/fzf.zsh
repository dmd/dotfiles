function setup_using_base_dir() {
    local fzf_base fzf_shell fzfdirs dir
    fzf_base=${HOME}/.fzf

    if [[ ! -d "${fzf_base}" ]]; then
        return 1
    fi

    fzf_shell="${fzf_base}/shell"

    # Setup fzf binary path
    if (( ! ${+commands[fzf]} )) && [[ "$PATH" != *$fzf_base/bin* ]]; then
        export PATH="$PATH:$fzf_base/bin"
    fi

    # Auto-completion
    if [[ -o interactive && "$DISABLE_FZF_AUTO_COMPLETION" != "true" ]]; then
        source "${fzf_shell}/completion.zsh" 2> /dev/null
    fi

    # Key bindings
    if [[ "$DISABLE_FZF_KEY_BINDINGS" != "true" ]]; then
        source "${fzf_shell}/key-bindings.zsh"
    fi
}

setup_using_base_dir 
unset -f  setup_using_base_dir 

if [[ -z "$FZF_DEFAULT_COMMAND" ]]; then
    if (( $+commands[rg] )); then
        export FZF_DEFAULT_COMMAND='rg --files --hidden'
    elif (( $+commands[fd] )); then
        export FZF_DEFAULT_COMMAND='fd --type f --hidden --exclude .git'
    elif (( $+commands[ag] )); then
        export FZF_DEFAULT_COMMAND='ag -l --hidden -g ""'
    fi
fi
