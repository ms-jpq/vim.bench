return {
  deps = {
    "nvim-yarp",
    "ncm2",
    "ncm2-bufword",
    "ncm2-path"
  },
  setup = function()
    vim.fn["ncm2#enable_for_buffer"]()
  end
}
