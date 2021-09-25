augroup HELLO
  autocmd!
  autocmd InsertEnter * lua TIMER.start()
  autocmd VimLeavePre * lua TIMER.fin()
augroup END
