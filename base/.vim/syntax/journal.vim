" Vim syntax file
" Language: journal
" Maintainer: Daniel Drucker
" Latest Revision: 26 Feb 2018

if exists("b:current_syntax")
	finish
endif


"highlight groups
syn match sep "^---$"
syn match time "\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d"
highlight sep ctermbg=blue
highlight time ctermbg=darkred

let b:current_syntax = "journal"


