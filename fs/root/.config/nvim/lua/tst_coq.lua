return {
  deps = {"coq_nvim"},
  setup = function()
    vim.g.coq_settings = {
      clients = {
        snippets = {
          warn = {}
        }
      }
    }
    require("coq")
    vim.cmd [[COQnow]]
  end
}
