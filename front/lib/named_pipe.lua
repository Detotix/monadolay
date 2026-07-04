
local json= require "lib/json"
local timer = require "lovr.timer"

local pipe={}

pipe.lp_pipe=nil

function pipe.openpipe()
    while not pipe.lp_pipe do
    pipe.lp_pipe = io.open("/tmp/monadolay_pipe_lp", "w")
    if not pipe.lp_pipe then
      print("[ MAIN (LOVR) ] waiting for writing pipe")
      lovr.timer.sleep(0.1)
    end
    print("[ MAIN (LOVR) ] writing pipe opened")
  end
end


function pipe.pipe_send(type,element)
    pipe.lp_pipe:write(json.encode({data_type=type, data_value=element}) .. "\n")
    pipe.lp_pipe:flush() 
end


function pipe.pipe_close(lppipe)
    lppipe:write("close" .. "\n")
    lppipe:flush() 
    timer.sleep(0.2)
    lppipe:close()
end

return pipe