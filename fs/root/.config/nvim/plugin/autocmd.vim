augroup HELLO
  autocmd!
  autocmd InsertEnter * lua TIMER.start()
  autocmd CompleteChanged * lua TIMER.done()
  autocmd VimLeavePre * lua TIMER.fin()
augroup END
