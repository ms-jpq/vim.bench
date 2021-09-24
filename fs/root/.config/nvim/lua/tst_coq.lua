local conf = {
  auto_start = true
}

return function(method)
  vim.g.coq_settings = conf
  require("coq")
end
