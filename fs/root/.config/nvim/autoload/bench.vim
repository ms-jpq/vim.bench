function! bench#comp_nvim() abort
  autocmd InsertEnter * lua require('completion').on_attach()
endfunction
