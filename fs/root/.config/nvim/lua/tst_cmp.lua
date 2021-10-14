return {
  deps = {
    "nvim-cmp",
    "cmp-buffer",
    "cmp-nvim-lsp",
    "cmp-path"
  },
  setup = function()
    require("cmp").setup {
      sources = {
        {name = "buffer"},
        {name = "path"},
        {name = "nvim_lsp"}
      }
    }
  end
}
