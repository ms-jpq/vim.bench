vim.opt.showmode = false
vim.opt.completeopt = {"noselect", "noinsert", "menuone"}
vim.opt.shortmess:append("c")

local lsp = require("lspconfig")
lspconfig.configs.wordbank_ls = {
  default_config = {
    cmd = {
      "/code/lsp/run.sh",
      "--cache",
      "--pool",
      vim.env.TST_LSP_INPUT
    },
    filetypes = {"clojure"},
    root_dir = function()
      return "/"
    end,
    settings = {}
  }
}

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

TIMER.done = function()
  local span = (time() - TIMER.mark) * 1000
  local info = vim.fn.complete_info {"mode", "items"}
  if info.mode == "eval" and #info.items > 0 and span > 1 then
    table.insert(TIMER.acc, span)
  end
end

TIMER.fin = function()
  if vim.env.TST_OUTPUT then
    local json = vim.fn.json_encode(TIMER.acc)
    vim.fn.writefile({json}, vim.env.TST_OUTPUT)
  end
end

require("tst_" .. vim.env.TST_FRAMEWORK)
