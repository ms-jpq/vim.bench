vim.g.completion_chain_complete_list = {
  {complete_items = {"lsp", "buffers", "path"}}
}

vim.schedule(
  function()
    require("completion").on_attach()
  end
)
