local _ = (function()
  vim.opt.showmode = false
  vim.opt.completeopt = {"noselect", "noinsert", "menuone"}
  vim.opt.shortmess:append("c")
  vim.opt.number = true
  vim.opt.timeoutlen = 500
end)()

local _ =
  (function()
  require("lspconfig/configs").wordbank_ls = {
    default_config = {
      cmd = {"/code/lsp/run.sh"},
      filetypes = {"clojure"},
      root_dir = function()
        return "/"
      end
    }
  }
  require("lspconfig").wordbank_ls.setup {}
end)()

local _ =
  (function()
  local framework = vim.env.TST_FRAMEWORK
  vim.validate {
    framework = {framework, "string"}
  }

  require("tst_" .. framework)
  print(">>>" .. framework .. "<<<")
end)()

local _ =
  (function()
  local output = vim.env.TST_OUTPUT
  vim.validate {output = {output, "string"}}

  local time = function()
    return vim.fn.reltimefloat(vim.fn.reltime())
  end

  TIMER = {}
  local mark, acc = nil, {}

  TIMER.start = function()
    vim.api.nvim_buf_attach(
      0,
      false,
      {
        on_lines = function()
          mark = time()
        end
      }
    )
  end

  TIMER.done = function()
    vim.validate {mark = {mark, "number"}}

    local span = (time() - mark) * 1000
    table.insert(acc, span)
  end

  TIMER.fin = function()
    local json = vim.fn.json_encode(acc)
    vim.fn.writefile({json}, output)
  end
end)()
