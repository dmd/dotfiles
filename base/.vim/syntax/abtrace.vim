" Vim syntax file
" Language: Ab Initio Trace File
" Maintainer: Daniel Drucker
" Latest Revision: 29 Dec 2017

if exists("b:current_syntax")
	finish
endif


syntax match Keyword "\v\="
syntax match Keyword "\v\*"
syntax match Keyword "\v\+"
"
"highlight groups
syn match Group0 /\v(^\s*(\S+\s+){0})@<=\S+/
syn match Group1 /\v(^\s*(\S+\s+){1})@<=\S+/
syn match Group2 /\v(^\s*(\S+\s+){2})@<=\S+/
syn match Group3 /\v(^\s*(\S+\s+){3})@<=\S+/
syn match Group4 /\v(^\s*(\S+\s+){4})@<=\S+/
highlight Group0 ctermfg=blue
highlight Group1 ctermfg=green
highlight Group2 ctermfg=yellow
highlight Group3 ctermfg=red
highlight Group4 ctermfg=blue

let b:current_syntax = "abtrace"


