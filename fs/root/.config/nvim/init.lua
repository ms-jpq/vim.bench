vim.opt.showmode = false

local lsp = require("lspconfig")
lsp.pyright.setup {}
lsp.tsserver.setup {}

print(">>>" .. vim.env.TST_FRAMEWORK .. "<<<")

local time = function()
  return vim.fn.reltimefloat(vim.fn.reltime())
end

TIMER = {}
TIMER.acc = {}

TIMER.start = function()
  vim.api.nvim_buf_attach(
    0,
    false,
    {
      on_lines = function()
        TIMER.mark = time()
      end
    }
  )
end

local comp = vim.fn.complete
vim.fn.complete = function(...)
  local span = (time() - TIMER.mark) * 1000
  table.insert(TIMER.acc, span)
  comp(...)
end

TIMER.fin = function()
  local json = vim.fn.json_encode(TIMER.acc)
  vim.fn.writefile({json}, vim.env.TST_OUTPUT)
end

require("tst_" .. vim.env.TST_FRAMEWORK)
