local conf = {
  auto_start = true
}

return function()
  vim.g.coq_settings = conf
  require("coq")
end
