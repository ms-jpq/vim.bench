NCM = function()
  vim.fn["ncm2#enable_for_buffer"]()

  local cont = nil
  cont = function()
    local clients = vim.lsp.buf_get_clients(0)
    for _, client in pairs(clients) do
      require("ncm2").register_lsp_source(client)
      return
    end
    vim.defer_fn(cont, 1)
  end
  cont()
end

vim.cmd [[autocmd BufEnter * lua NCM()]]
