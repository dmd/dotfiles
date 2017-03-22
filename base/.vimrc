set nocp
filetype off
let $GIT_SSL_NO_VERIFY = 'true'

if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $HOME/.vimrc
endif
call plug#begin('~/.vim/plugged')
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'ervandew/supertab'
Plug 'airblade/vim-gitgutter'
Plug 'bling/vim-bufferline'
call plug#end()

let g:airline_theme='murmur'
let g:airline#extensions#hunks#enabled=0  "don't put changes in statusbar

if has('gui_running') || &t_Co > 2
  set background=dark
  syntax enable
  colorscheme torte
  if has('mac')
      set guifont=monaco:h12
  elseif has('gui_gtk2')
      set guifont=Inconsolata\ 20
      set guioptions-=T  "no toolbar
  endif
endif

highlight LineNr ctermfg=240 ctermbg=233 guifg=#585858 guibg=#121212

set tags=./tags;/
set hidden  "allow opening a new buffer, hiding the old one
set history=1000
set backspace=indent,eol,start
set hlsearch incsearch showmatch
set smarttab tabstop=4 shiftwidth=4 softtabstop=4 expandtab
set number
" set cursorline
set nojoinspaces
set encoding=utf8
set ignorecase smartcase
set wildmenu wildmode=list:longest
set scrolloff=3
set clipboard=unnamed
set foldmethod=syntax
set foldlevelstart=20

set visualbell
set modeline
set shortmess=aoOtTI
set laststatus=2
set ruler
set showcmd

" jk as ESC
inoremap jk <ESC>

" disable Ex mode
nnoremap Q <nop>

" the trailing // makes it more better.
set directory=/tmp//

au BufRead,BufNewFile *.dml       set filetype=dml
au BufRead,BufNewFile *.dmlscript set filetype=dml
au BufRead,BufNewFile *.xfr       set filetype=dml

" execute m_eval on region
inoremap <F5> <ESC>V<bar>:!vimev<CR><bar>G
noremap <F5> V<bar>:!vimev<CR><bar>G

" enable mouse
set mouse=a
