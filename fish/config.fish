set fish_greeting
set -x TZ America/New_York
set -Ux EDITOR emacs
set -Ux VISUAL $EDITOR
set -Ux LESS -r
set -Ux HOMEBREW_AUTO_UPDATE_SECS 86400
set -Ux FZF_DEFAULT_OPTS '--reverse --border --exact --height=50%'
set -Ux AWS_PAGER ""
set -Ux TERM xterm-256color
set -x OPENAI_API_KEY (cat ~/.openai-api-key)
fish_config theme choose "ayu Dark"

fish_add_path ~/bin ~/.cargo/bin ~/.local/bin /opt/homebrew/bin /usr/local/bin /sbin /usr/local/sbin

abbr ... 'cd ../..'
abbr e 'emacs -nw'
abbr gc 'git commit'
abbr gr 'git checkout --'
abbr gs 'git status'
abbr --query s ; or abbr s 'sudo fish' # don't override cluster snippet
abbr sci 'ssh-copy-id'
abbr ta 'tmux attach'
alias j 'z'
alias ji 'zi'
alias ls (if test (uname) = 'Darwin'; echo 'ls -G'; else; echo 'ls --color=tty'; end)
if command diff --color . . >/dev/null 2>&1
    abbr diff 'diff --color'
end

switch (hostname | string split -m 1 '.')[1]
    case dev
        abbr irc 'rm $HOME/.weechat/weechat.log; weechat'
    case atto zepto dromedary ddrucker-mba ogawa
        abbr m 'ssh ddrucker@mickey.mclean.harvard.edu'
        abbr n 'ssh root@nisaba.mclean.harvard.edu'
        abbr x 'ssh root@x5backup.mclean.harvard.edu'
        abbr o 'ssh ddrucker@ogawa.mclean.harvard.edu'
        abbr pluto 'ssh ddrucker@pluto.mclean.harvard.edu'
    case mickey
        abbr ssj 'scontrol show job'
end

test -e "$HOME/.iterm2_shell_integration.fish"; and source "$HOME/.iterm2_shell_integration.fish"
zoxide init fish | source

set -gx STARSHIP_CONFIG $HOME/dotfiles/starship.toml
starship init fish | source

