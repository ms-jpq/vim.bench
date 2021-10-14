local _ = (function()
  vim.opt.showmode = false
  vim.opt.completeopt = {"noselect", "noinsert", "menuone"}
  vim.opt.shortmess:append("c")
end)()

local _ =
  (function()
  local lsp_cache = vim.env.TST_LSP_CACHE
  local lsp_input = vim.env.TST_LSP_INPUT
  vim.validate {
    lsp_cache = {lsp_cache, "string"},
    lsp_input = {lsp_input, "string"}
  }

  require("lspconfig/configs").wordbank_ls = {
    default_config = {
      cmd = {
        "/code/lsp/run.sh",
        "--cache",
        lsp_cache,
        "--pool",
        lsp_input
      },
      filetypes = {"clojure"},
      root_dir = function()
        return "/"
      end,
      settings = {}
    }
  }
  require("lspconfig").wordbank_ls.setup {}
end)()

local _ =
  (function()
  local framework = vim.env.TST_FRAMEWORK
  vim.validate {framework = {framework, "string"}}
  print(">>>" .. framework .. "<<<")

  local spec = require("tst_" .. framework)
  vim.validate {
    deps = {spec.deps, "table"},
    setup = {spec.setup, "function"}
  }

  vim.schedule(
    function()
      for key, val in pairs(spec.deps) do
        vim.validate {
          key = {key, "number"},
          val = {val, "string"}
        }
        vim.cmd("packadd " .. val)
      end
      vim.schedule(spec.setup)
    end
  )
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
    local info = vim.fn.complete_info {"mode", "items"}
    if info.mode == "eval" and #info.items > 0 and span > 1 then
      table.insert(acc, span)
    end
  end

  TIMER.fin = function()
    local json = vim.fn.json_encode(acc)
    vim.fn.writefile({json}, output)
  end
end)()
