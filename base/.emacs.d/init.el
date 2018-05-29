(setq auto-save-list-file-prefix nil)
(menu-bar-mode 0)
(setq auto-mode-alist (append '(("\\.run$" . xxtrace-mode)) auto-mode-alist))

(let ((xxtrace-highlight "/u/saletnik/public/xxtrace.el"))
 (when (file-exists-p xxtrace-highlight)
   (load-file xxtrace-highlight))
)


(defalias 'yes-or-no-p 'y-or-n-p)

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(inhibit-startup-screen t)
 '(xterm-mouse-mode t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
(put 'upcase-region 'disabled nil)
