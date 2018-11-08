set nocp
"set clipboard=exclude:.*   " use this if below makes startup slow
set clipboard=unnamed  " is really slow
let mapleader = ","

" Plugins
if empty(glob('~/.vim/autoload/plug.vim'))
    silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    autocmd VimEnter * PlugInstall --sync | source $HOME/.vimrc
endif
call plug#begin('~/.vim/plugged')
    Plug 'zxqfl/tabnine-vim'
    Plug 'vim-airline/vim-airline'
    Plug 'vim-airline/vim-airline-themes'
    Plug 'vim-scripts/showhide.vim'        " zs show zh hide word under cursor :SHOW :HIDE zn open all
    "Plug 'ervandew/supertab'               " tab completion of words
    Plug 'airblade/vim-gitgutter'          " git changes in gutter
    Plug 'fidian/hexmode'                  " :Hexmode
    Plug 'dmd/vim-rsi'                     " readline style insertion, C-a C-e etc.
    Plug 'ConradIrwin/vim-bracketed-paste' " automatically set paste
call plug#end()

" better % matching
runtime macros/matchit.vim

let g:airline_theme='murmur'
let g:airline#extensions#hunks#enabled=0  "don't put changes in statusbar

" Enable the list of buffers (with just filename)
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#fnamemod = ':t'

syntax enable
if has('gui_running') || &t_Co > 2
    set background=dark
    colorscheme torte
    if has('gui_gtk2')
        set guifont=Inconsolata\ 20
        set guioptions-=T  "no toolbar
    endif
endif

highlight LineNr ctermfg=240 ctermbg=233 guifg=#585858 guibg=#121212


set display+=lastline                  " don't show @ for long lines
set encoding=utf-8
set autoindent                         " Indent at the same level of the previous line
set backspace=indent,eol,start         " Backspace for dummies

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
set mouse+=a                           " Automatically enable mouse usage
set ttymouse=xterm2                    " drag around vim splits inside tmux splits
set mousehide                          " Hide the mouse cursor while typing
set nojoinspaces
set scrolljump=5                       " Line to scroll when cursor leaves screen
set scrolloff=3                        " Minumum lines to keep above and below cursor
set shortmess=aoOtTI
set showcmd                            " Show partial commands in status line and Selected characters/lines in visual mode
set showmatch                          " Show matching brackets/parentthesis
set visualbell
set whichwrap+=<,>,h,l                 " Allow backspace and cursor keys to cross line boundaries
set wildignore+=*/tmp/*,*.o,*.obj,*.so,*swp,*.class,*.pyc,*.png,*.jpg,*.gif,*.zip
set wildmenu                           " Show list instead of just completing
set wildmode=list:longest,full
set updatetime=800                     " make gitgutter and others update faster

" hybrid line numbering
if v:version > 703
    set number relativenumber
    augroup numbertoggle
        autocmd!
        autocmd BufEnter,FocusGained,InsertLeave * set relativenumber
        autocmd BufLeave,FocusLost,InsertEnter   * set norelativenumber
    augroup END
endif

" Visual shifting (does not exit Visual mode)
vnoremap < <gv
vnoremap > >gv

" jk as ESC
inoremap jk <ESC>

" disable Ex mode
nnoremap Q <nop>

" the trailing // makes it use complete path (foo/bar becomes foo%bar)
set directory=/tmp//

au BufRead,BufNewFile *.dml       set filetype=dml
au BufRead,BufNewFile *.dmlscript set filetype=dml
au BufRead,BufNewFile *.xfr       set filetype=dml
au BufRead,BufNewFile *.run       set filetype=abtrace
au BufRead,BufNewFile *.ircsearch set filetype=ircsearch
au BufRead,BufNewFile *.jrn       set filetype=journal

" execute m_eval on region
inoremap <F5> <ESC>V<bar>:!vimev<CR><bar>G
noremap <F5> V<bar>:!vimev<CR><bar>G

" n always goes forward, N always goes backwards
nnoremap <expr> n  'Nn'[v:searchforward]
nnoremap <expr> N  'nN'[v:searchforward]

" clear matches, update syntax highlighting in C-l
nnoremap <c-l> :nohlsearch<cr>:diffupdate<cr>:syntax sync fromstart<cr><c-l>

" always jump to line number if present
nnoremap gf gF
