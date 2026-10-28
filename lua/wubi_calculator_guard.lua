-- SPDX-License-Identifier: CC0-1.0
-- Keep upstream calculation/yield behavior; incomplete expressions produce no error log.
local calculator = require("calculator")

return function(input, segment, env)
  -- Lua 5.4 permits a translator to yield candidates through pcall.
  -- This contains runtime errors; it does not sandbox the upstream calculator.
  pcall(calculator, input, segment, env)
end
