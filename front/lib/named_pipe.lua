
local json= require "lib/json"
local shared= require "shared"
local timer = require "lovr.timer"

local pipe={}

function pipe.pipe_send(lppipe,type,element)
    lppipe:write(json.encode({data_type=type, data_value=element}) .. "\n")
    lppipe:flush() 
end
function pipe.pipe_close(lppipe)
    lppipe:write("close" .. "\n")
    lppipe:flush() 
    timer.sleep(0.2)
    lppipe:close()
end

return pipe