(let ((gc-cons-threshold most-positive-fixnum))
  (add-hook 'after-init-hook
            (lambda () (setq gc-cons-threshold 1600000)))
;;  (cua-mode)
  (setq initial-major-mode 'fundamental-mode)
  (setq-default inhibit-startup-screen t)
  (setq inhibit-splash-screen t)
  (setq inhibit-startup-message t)
  (setq initial-scratch-message "")

  (setq-default indent-tabs-mode nil)
  (setq vc-follow-symlinks t)
  (fset 'yes-or-no-p 'y-or-n-p)

  ;; don't litter
  (setq save-place-file (concat user-emacs-directory "places")
        backup-directory-alist `(("." . ,(concat user-emacs-directory
                                                 "backups"))))
  (setq auto-save-file-name-transforms
        `((".*" ,temporary-file-directory t)))

  ;; Support the mouse and colors in the terminal
  (xterm-mouse-mode 1)

  ;; (menu-bar-mode 0)

  (require 'package)
  (add-to-list 'package-archives
               '("melpa" . "https://melpa.org/packages/"))
  (package-initialize)
  (unless (package-installed-p 'use-package)
    (package-refresh-contents)
    (package-install 'use-package))
  (setq use-package-always-ensure t)

  (require 'use-package)

  (load-theme 'tango-dark)
  (add-to-list 'default-frame-alist '(background-color . "black"))

  (use-package smart-tab
    :ensure t
    :config
    (global-smart-tab-mode))

  (use-package ido
    :ensure t
    :config
    ;; smex is a better replacement for M-x
    (use-package smex
      :ensure t
      :bind
      ("M-x" . smex)
      ("M-X" . smex-major-mode-commands))

    ;; This makes ido work vertically
    (use-package ido-vertical-mode
      :ensure t
      :config
      (setq ido-vertical-define-keys 'C-n-C-p-up-down-left-right
            ido-vertical-show-count t)
      (ido-vertical-mode 1))

    ;; This adds flex matching to ido
    (use-package flx-ido
      :ensure t
      :config
      (flx-ido-mode 1)
      (setq ido-enable-flex-matching t
            flx-ido-threshold 1000))

    ;; Turn on ido everywhere we can
    (ido-mode 1)
    (ido-everywhere 1)

    (setq resize-mini-windows t
          ido-use-virtual-buffers t
          ido-auto-merge-work-directories-length -1)
    )
  )
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(package-selected-packages '(flx-ido ido-vertical-mode smex smart-tab)))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
