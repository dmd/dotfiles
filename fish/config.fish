set fish_greeting
set -x TZ America/New_York
set -Ux EDITOR emacs
set -Ux VISUAL $EDITOR
set -Ux LESS -r
set -Ux HOMEBREW_AUTO_UPDATE_SECS 86400
set -Ux FZF_DEFAULT_OPTS '--reverse --border --exact --height=50%'
set -Ux AWS_PAGER ""
set -Ux TERM xterm-256color
set -gx STARSHIP_CONFIG $HOME/dotfiles/starship.toml

fish_add_path ~/bin ~/.cargo/bin ~/.local/bin /opt/homebrew/bin /usr/local/bin /sbin /usr/local/sbin

abbr e 'emacs -nw'
abbr ta 'tmux attach'
alias j 'z'
alias ji 'zi'
abbr ... 'cd ../..'
abbr edges 'ssh edges@3e.org'
abbr sci 'ssh-copy-id'
abbr s 'sudo fish'

abbr gs 'git status'
abbr gc 'git commit'
abbr gr 'git checkout --'

switch (hostname | string split -m 1 '.')[1]
    case dev
        abbr irc 'rm $HOME/.weechat/weechat.log; weechat'
    case atto zepto dromedary ddrucker-mba ogawa
        abbr m 'ssh ddrucker@micc.mclean.harvard.edu -t "sh -c \'exec fish -li\'"'
        abbr mk 'ssh ddrucker@mickey.mclean.harvard.edu -t "sh -c \'exec fish -li\'"'
        abbr n 'ssh root@nisaba.mclean.harvard.edu'
        abbr x 'ssh root@x5backup.mclean.harvard.edu'
        abbr o 'ssh ddrucker@ogawa.mclean.harvard.edu'
        abbr pluto 'ssh ddrucker@pluto.mclean.harvard.edu'
end

# Cluster-specific configuration
if test -d /cm/shared
    function dcm_run
        singularity run -B /data -B /home -B /n /cm/shared/singularity/images/dcm.sif $argv
    end
    abbr dcmodify 'dcm_run dcmodify'
    abbr dcmdump 'dcm_run dcmdump'
    abbr storescu 'dcm_run storescu'
    abbr dcmsend 'dcm_run dcmsend'
    abbr s 'sudo bash'

    if test -f /cm/shared/.cluster-name-mickey
       alias q 'squeue -o "%.10i %.9u %.10j %.8T %.6C %12N %.10M %.20l"'
       alias qu 'squeue -u $USER -o "%.10i %.9u %.10j %.8T %.6C %12N %.10M %.20l"'
       alias slacct 'sacct --format JobName%15,JobID,TimelimitRaw,TotalCPU,MaxRSS,MaxVMSize,MaxPages,Elapsed,State,Nodelist --units=G'
       eval /cm/shared/anaconda3/bin/conda "shell.fish" "hook" $argv | source
    else
       alias q 'qstat -u "*"'
    end
end

test -e "$HOME/.iterm2_shell_integration.fish"; and source "$HOME/.iterm2_shell_integration.fish"

starship init fish | source

if test (uname) = 'Darwin'
    alias ls 'ls -G'
else
    alias ls 'ls --color=tty'
end

if command diff --color . . >/dev/null 2>&1
    abbr diff 'diff --color'
end
fish_config theme choose "ayu Dark"
zoxide init fish | source
