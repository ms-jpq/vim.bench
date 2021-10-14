vim.g.completion_confirm_key = "<cr>"
vim.g.completion_disable_filetypes = {}
vim.g.completion_chain_complete_list = {
  {
    complete_items = {
      "lsp",
      "buffers",
      "path"
    }
  }
}
require("completion").on_attach()
