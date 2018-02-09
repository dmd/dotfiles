" Vim syntax file
" Language: IRC Search
" Maintainer: Daniel Drucker
" Latest Revision: 9 Feb 2018

if exists("b:current_syntax")
	finish
endif


"highlight groups
syn match filename "^[^:]*" nextgroup=linenum
syn match linenum  ":[^:]*"  contained nextgroup=time
syn match time ":..:.. <*"he=e-1 contained 
highlight filename ctermfg=blue
highlight linenum ctermfg=black
highlight time ctermfg=black
"highlight nick ctermfg=blue

let b:current_syntax = "ircsearch"


