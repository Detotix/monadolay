local named_pipe = require 'lib/named_pipe'
local shared = require 'shared'
local menu = require 'parts/menu'
local boundaries = require 'parts/boundaries'
local drender = require 'parts/default_render'
local ffi = require("ffi") 
ffi.cdef[[ 
  int getpid(void); 
]]
local time=0
function lovr.load()
  local pid=ffi.C.getpid()
  print("[ MAIN (LOVR) ] Starting LÖVR application")
  print("[ MAIN (LOVR) ] path "..lovr.filesystem.getSource())

  named_pipe.openpipe()
  
  named_pipe.pipe_send("pid", {pid})

  Pipe_channel = lovr.thread.getChannel('pipe_channel')
  local thread = lovr.thread.newThread(assert(io.open(lovr.filesystem.getSource().."/threads/named_pipe.lua","rb")):read("*a"))
  thread:start()

end

function lovr.draw(pass)
  for i, func in ipairs(shared.conditioned_renderfunctions) do
    if func[3]==shared.data[func[2]] or func[3]==shared.localdata[func[2]] then
      func[1](pass)
    end
  end
  for index, value in ipairs(shared.render["render"]) do
    shared.renderfunctions[value](pass) 
  end
end

local function merge_shallow(target, source)
  for k, v in pairs(source) do
    target[k] = v
  end
end

function lovr.update(dt)
  while Pipe_channel:peek() do
    local message = Pipe_channel:pop()
    if message["data_type"]=="position" then
      merge_shallow(shared.positioning,message["data_value"])
    elseif message["data_type"]=="settings" then
      merge_shallow(shared.settings, message["data_value"])
    elseif message["data_type"]=="render" then
      merge_shallow(shared.render, message["data_value"])
    elseif message["data_type"]=="data" then
      merge_shallow(shared.data, message["data_value"])
    elseif message["data_type"]=="monado_task_result" then
      local table={}
      table[message["data_value"]["type"]]=message["data_value"]["result"]
      merge_shallow(shared.monado_results, table)
    end
    message=nil
  end
  -- if (os.clock()>time) then
  --   time=os.clock()+0.035
  --   pcall(function()
  --     status, webdata, headers = http.request("http://localhost:1469")
  --     shared.data=json.decode(webdata)
  --     if shared.data["datachange"] then
  --       status2, webdata2, headers2 = http.request("http://localhost:1469/position")
  --       shared.positioning=json.decode(webdata2)
  --       status2, webdata2, headers2 = http.request("http://localhost:1469/settings")
  --       shared.settings=json.decode(webdata2)
  --       status2, webdata2, headers2 = http.request("http://localhost:1469/render")
  --       shared.render=json.decode(webdata2)
  --     end
  --     if shared.data["requestpid"] then
  --       local pid=ffi.C.getpid()
  --       http.request("http://localhost:1469/pid/"..pid)
  --     end
  --   end)
  --end
end