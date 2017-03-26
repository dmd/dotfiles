set nocp
set clipboard=exclude:.*  "set clipboard=unnamed  is really slow

" Plugins
if empty(glob('~/.vim/autoload/plug.vim'))
    silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    autocmd VimEnter * PlugInstall --sync | source $HOME/.vimrc
endif
call plug#begin('~/.vim/plugged')
    Plug 'vim-airline/vim-airline'
    Plug 'vim-airline/vim-airline-themes'
    Plug 'ervandew/supertab'              " tab completion of words
    Plug 'airblade/vim-gitgutter'         " git changes in gutter
    Plug 'bling/vim-bufferline'           " multiple buffers listed in line
    Plug 'fidian/hexmode'                 " :Hexmode
    Plug 'mhinz/vim-startify'             " start menu
    Plug 'tpope/vim-rsi'                  " readline style insertion, C-a C-e etc.
    Plug 'terryma/vim-multiple-cursors'   " C-n for multiple cursors on match
call plug#end()

let g:airline_theme='murmur'
let g:airline#extensions#hunks#enabled=0  "don't put changes in statusbar
let g:startify_custom_header =['Welcome to vim!']

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


set encoding=utf-8
set autoindent                         " Indent at the same level of the previous line
set backspace=indent,eol,start         " Backspace for dummies
set cursorline                         " Highlight current line

set expandtab                          " Tabs are spaces, not tabs
set smarttab                           " Smart tab
set softtabstop=4                      " Let backspace delete indent
set tabstop=4                          " An indentation every four columns
set shiftwidth=4                       " Use indents of 4 spaces

set fileformats=unix,dos,mac           " Use Unix as the standard file type
set foldlevelstart=99
set foldmethod=syntax
set hidden                             " Allow buffer switching without saving
set history=10000

set hlsearch                           " Highlight search terms
set ignorecase                         " Case insensitive search
set smartcase                          " ... but case sensitive when uc present
set incsearch                          " Find as you type search

set laststatus=2                       " Always show status line
set matchtime=5                        " Show matching time
set modeline
set mouse=a                            " Automatically enable mouse usage
set mousehide                          " Hide the mouse cursor while typing
set nojoinspaces
set number                             " Line numbers on
set relativenumber                     " Relative numbers on
set ruler                              " Show the ruler
set scrolljump=5                       " Line to scroll when cursor leaves screen
set scrolloff=3                        " Minumum lines to keep above and below cursor
set shortmess=aoOtTI
set showcmd                            " Show partial commands in status line and Selected characters/lines in visual mode
set showmatch                          " Show matching brackets/parentthesis
set tags=./tags;/
set visualbell
set whichwrap+=<,>,h,l                 " Allow backspace and cursor keys to cross line boundaries
set wildignore+=*/tmp/*,*.o,*.obj,*.so,*swp,*.class,*.pyc,*.png,*.jpg,*.gif,*.zip
set wildmenu                           " Show list instead of just completing
set wildmode=list:longest,full


" Visual shifting (does not exit Visual mode)
vnoremap < <gv
vnoremap > >gv

" :W sudo saves the file
" (useful for handling the permission-denied error)
command! W w !sudo tee % > /dev/null

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

