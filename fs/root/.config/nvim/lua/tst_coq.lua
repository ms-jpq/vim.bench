local conf = {
  auto_start = true
}

require("coq")

return function(method)
  vim.g.coq_settings = conf
end
