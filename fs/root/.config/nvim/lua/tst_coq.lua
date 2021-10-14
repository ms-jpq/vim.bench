return {
  deps = {"coq_nvim"},
  setup = function()
    vim.g.coq_settings = {
      auto_start = true,
      display = {
        pum = {
          fast_close = false
        }
      }
    }
    require("coq")
  end
}
