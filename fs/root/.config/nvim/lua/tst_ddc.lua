vim.fn["ddc#custom#patch_global"](
  "sources",
  {
    "around",
    "nvim-lsp",
    "file"
  }
)
vim.fn["ddc#custom#patch_global"](
  "sourceOptions",
  {
    _ = {
      matchers = {"matcher_head"},
      sorters = {"sorter_rank"}
    }
  }
)
