" Vim syntax file
" Language: DML
" Maintainer: Bill Zimmerman
" Latest Revision: 29 Sep 2014

if exists("b:current_syntax")
	finish
endif


" dml Keywords
syntax keyword dmlFunction begin end record block

syntax keyword dmlKeyword if else while result
syntax keyword dmlKeyword let type member
syntax keyword dmlKeyword reinterpret_as exit

syntax keyword dmlType constant vector string decimal unsigned int
syntax keyword dmlType integer long date datetime void double float
syntax keyword dmlType ascii utf8 big little endian NULL

syntax keyword dmlOperator not or and 

" dml Matches
syntax match dmlOperator "\v\&\&"
syntax match dmlOperator "\v\|\|"
syntax match dmlOperator "\v\="
syntax match dmlOperator "\v\*"
syntax match dmlOperator "\v/"
syntax match dmlOperator "\v\+"
syntax match dmlOperator "\v\-"
syntax match dmlOperator "\v\?"
syntax match dmlOperator "\v\>"
syntax match dmlOperator "\v\<"
syntax match dmlOperator "\v\>\="
syntax match dmlOperator "\v\<\="
syntax match dmlOperator "\v\:\:"
syntax match dmlOperator "\v\!\="

syntax match dmlComment "\v\/\/.*$"


" dml Regions
syntax region dmlString start=/\v"/ skip=/\v\\./ end=/\v"/

syntax region dmlComment start=/\v\/\*/ end=/\v\*\//


" Highlight links
highlight link dmlFunction Define
highlight link dmlKeyword  Keyword
highlight link dmlType     Type
highlight link dmlComment  Comment
highlight link dmlOperator Operator
highlight link dmlString   String


let b:current_syntax = "dml"


" vim: set undofile:
