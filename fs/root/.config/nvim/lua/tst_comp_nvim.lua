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
