vim.opt.showmode = false

local lsp = require("lspconfig")
lsp.pyright.setup {}
lsp.tsserver.setup {}

print(vim.env.TST_FRAMEWORK .. " >>> " .. vim.env.TST_METHOD)

TIMER = {}
TIMER.acc = {}

TIMER.start = function()
  vim.api.nvim_buf_attach(
    0,
    false,
    {
      on_lines = function()
        TIMER.mark = vim.fn.localtime()
      end
    }
  )
end

local comp = vim.fn.complete
vim.fn.complete = function(...)
  local span = vim.fn.localtime() - TIMER.mark
  table.insert(TIMER.acc, span)
  comp(...)
end

TIMER.fin = function()
  local json = vim.fn.json_encode(TIMER.acc)
  vim.fn.writefile({json}, vim.env.TST_OUTPUT)
end

require("tst_" .. vim.env.TST_FRAMEWORK)(vim.env.TST_METHOD)
