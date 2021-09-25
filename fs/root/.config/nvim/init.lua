vim.opt.showmode = false

local lsp = require("lspconfig")
lsp.pyright.setup {}
lsp.tsserver.setup {}

print(vim.env.TST_FRAMEWORK .. " >>> " .. vim.env.TST_METHOD)

TIMER = {}

local acc = {}

TIMER.start = function()
  vim.api.nvim_buf_attach(
    0,
    false,
    {
      on_lines = function()
        TIMER.mark = vim.loop.now()
      end
    }
  )
end

TIMER.done = function()
  local span = vim.loop.now() - TIMER.mark
  local info = vim.fn.complete_info()
  if info.mode == "eval" and info.pum_visible then
    table.insert(acc, span)
  end
end

TIMER.fin = function()
  local json = vim.fn.json_encode(acc)
  vim.fn.writefile({json}, vim.env.TST_OUTPUT)
end

require("tst_" .. vim.env.TST_FRAMEWORK)(vim.env.TST_METHOD)
