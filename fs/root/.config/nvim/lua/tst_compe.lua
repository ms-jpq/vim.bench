return {
  deps = {
    "nvim-compe"
  },
  setup = function()
    require("compe").setup {
      source = {
        nvim_lsp = true,
        buffer = true,
        path = true
      }
    }
  end
}
