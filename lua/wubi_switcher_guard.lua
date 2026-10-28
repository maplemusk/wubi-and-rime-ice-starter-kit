-- SPDX-License-Identifier: CC0-1.0
-- Delegate source menu behavior, letting normal key processing continue on source errors.
local switcher = require("switcher")
local guard = {}

function guard.init(env)
  local ready = true
  if type(switcher.init) == "function" then
    ready = pcall(switcher.init, env)
  end
  env._wubi_switcher_guard_ready = ready
end

function guard.func(key, env)
  if not env._wubi_switcher_guard_ready then
    return 2
  end
  local ok, result = pcall(switcher.func, key, env)
  if ok and (result == 0 or result == 1 or result == 2) then
    return result
  end
  return 2
end

function guard.fini(env)
  if type(switcher.fini) == "function" then
    pcall(switcher.fini, env)
  end
  env._wubi_switcher_guard_ready = nil
end

return guard
