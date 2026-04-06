local shared = require 'shared'
local boundaries = require 'parts/boundaries'
local menu = require 'parts/menu'
local function reg()
	shared.renderfunctions["menu"] = menu.render
end

function lovr.conf(t)
	t.headset.overlay = 6
    t.window=false
	t.identity = "monadolay"
	reg()
end
