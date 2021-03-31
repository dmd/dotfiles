(setq-default inhibit-startup-screen t)
(setq inhibit-splash-screen t)
(setq inhibit-startup-message t)
(setq initial-scratch-message "")
(setq initial-major-mode 'fundamental-mode)

(require 'package)
(add-to-list 'package-archives
             '("melpa" . "https://melpa.org/packages/"))
(package-initialize)
(unless (package-installed-p 'use-package)
  (package-refresh-contents)
  (package-install 'use-package))
(setq use-package-always-ensure t)

;; (use-package benchmark-init
;;   :ensure t
;;   :config
;;   ;; To disable collection of benchmark data after init is done.
;;   (add-hook 'after-init-hook 'benchmark-init/deactivate))

(use-package diminish)

(eval-when-compile
  (defvar use-package-verbose t)
  (require 'use-package))

(load-theme 'tango-dark)
(add-to-list 'default-frame-alist '(background-color . "black"))

(column-number-mode 1)
(line-number-mode 1)


(use-package smart-mode-line
  :config
  (setq sml/no-confirm-load-theme t
        sml/theme 'light)
  (sml/setup))

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(package-selected-packages
   '(neotree diff-hl smooth-scrolling flx-ido ido-vertical-mode smex smart-mode-line use-package diminish expand-region)))

(setq vc-follow-symlinks t)

(use-package ido
  :config
  ;; smex is a better replacement for M-x
  (use-package smex
    :bind
    ("M-x" . smex)
    ("M-X" . smex-major-mode-commands))


  ;; This makes ido work vertically
  (use-package ido-vertical-mode
    :config
    (setq ido-vertical-define-keys 'C-n-C-p-up-down-left-right
          ido-vertical-show-count t)
    (ido-vertical-mode 1))

  ;; This adds flex matching to ido
  (use-package flx-ido
    :config
    (flx-ido-mode 1)
    (setq ido-enable-flex-matching t
          flx-ido-threshold 1000))

  ;; Turn on ido everywhere we can
  (ido-mode 1)
  (ido-everywhere 1)

  (setq resize-mini-windows t
        ido-use-virtual-buffers t
        ido-auto-merge-work-directories-length -1))

(use-package smooth-scrolling
  :config
  (setq smooth-scroll-margin 5
        scroll-conservatively 101
        scroll-preserve-screen-position t
        auto-window-vscroll nil
        scroll-margin 5)
  (smooth-scrolling-mode 1))

(use-package expand-region
  :bind ("C-\\" . er/expand-region))


;; Ensure backups make it to a different folder so we don't litter all
;; our directories with them.
(setq save-place-file (concat user-emacs-directory "places")
      backup-directory-alist `(("." . ,(concat user-emacs-directory
                                               "backups"))))
(setq auto-save-file-name-transforms
      `((".*" ,temporary-file-directory t)))

;; Make it so you only need to type 'y' or 'n' not 'yes' or 'no'
(fset 'yes-or-no-p 'y-or-n-p)

;; Support the mouse and colors in the terminal
(xterm-mouse-mode 1)

(set-background-color "black")
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
