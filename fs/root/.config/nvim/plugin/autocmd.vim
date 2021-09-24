augroup HELLO
  autocmd!
  autocmd InsertCharPre * lua TIMER.mark = vim.loop.now()
  autocmd CompleteChanged * lua TIMER.done()
  autocmd VimLeavePre * lua TIMER.fin()
augroup END
