vim.g.completion_chain_complete_list = {
  default = {
    {complete_items = {"lsp"}},
    {complete_items = {"buffers"}},
    {complete_items = {"path"}}
  }
}
vim.fn["bench#comp_nvim"]()
