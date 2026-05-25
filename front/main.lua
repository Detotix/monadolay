local json = require 'lib/json'
local named_pipe = require 'lib/named_pipe'
local http = require 'http'
local shared = require 'shared'
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

  local pipe = nil
  while not pipe do
    pipe = io.open("/tmp/monadolay_pipe_lp", "w")
    if not pipe then
      print("[ MAIN (LOVR) ] waiting for writing pipe")
      lovr.timer.sleep(0.1)
    end
    print("[ MAIN (LOVR) ] writing pipe opened")
  end
  named_pipe.pipe_send(pipe,"pid", {pid})
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


function lovr.update(dt)

  if (os.clock()>time) then
    time=os.clock()+0.035
    pcall(function()
      status, webdata, headers = http.request("http://localhost:1469")
      shared.data=json.decode(webdata)
      if shared.data["datachange"] then
        status2, webdata2, headers2 = http.request("http://localhost:1469/position")
        shared.positioning=json.decode(webdata2)
        status2, webdata2, headers2 = http.request("http://localhost:1469/settings")
        shared.settings=json.decode(webdata2)
        status2, webdata2, headers2 = http.request("http://localhost:1469/render")
        shared.render=json.decode(webdata2)
      end
      if shared.data["requestpid"] then
        local pid=ffi.C.getpid()
        http.request("http://localhost:1469/pid/"..pid)
      end
    end)
  end
end