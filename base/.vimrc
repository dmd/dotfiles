set nocp
filetype off
let $GIT_SSL_NO_VERIFY = 'true'

if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $HOME/.vimrc
endif
call plug#begin('~/.vim/plugged')
Plug 'bling/vim-airline'
Plug 'ervandew/supertab'
call plug#end()

let g:airline#extensions#whitespace#enabled = 0

if has('gui_running') || &t_Co > 2
  set background=dark
  syntax enable
  colorscheme torte
  if has('mac')
      set guifont=monaco:h13
  elseif has('gui_gtk2')
      set guifont=Inconsolata\ 20
      set guioptions-=T  "no toolbar
  endif
endif

highlight LineNr ctermfg=240 ctermbg=233 guifg=#585858 guibg=#121212

set tags=./tags;/
set history=1000
set backspace=indent,eol,start
set hlsearch incsearch showmatch
set smarttab tabstop=4 shiftwidth=4 softtabstop=4 expandtab
set number
set nojoinspaces
set encoding=utf8
set ignorecase smartcase
set wildmenu wildmode=list:longest
set scrolloff=2
set clipboard=unnamed
set foldmethod=syntax
set foldlevelstart=20

set visualbell
set modeline
set shortmess=aoOtTI
set laststatus=2
set ruler
set showcmd

" kj/jk as ESC
inoremap jk <ESC>
inoremap kj <ESC>

"disable Ex mode
nnoremap Q <nop>

" the trailing // makes it more better.
set directory=/tmp//

au BufRead,BufNewFile *.dml       set filetype=dml
au BufRead,BufNewFile *.dmlscript set filetype=dml
au BufRead,BufNewFile *.xfr       set filetype=dml
