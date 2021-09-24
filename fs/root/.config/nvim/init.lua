print(vim.env.TST_FRAMEWORK .. " >>> " .. vim.env.TST_METHOD)

TIMER = {}

local acc = {}

TIMER.done = function()
  local span = vim.loop.now() - TIMER.mark
  table.insert(acc, span)
end

TIMER.fin = function()
  local json = vim.fn.json_encode(acc)
  vim.fn.writefile({json}, vim.env.TST_OUTPUT)
end
