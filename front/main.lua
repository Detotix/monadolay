local json = require 'lib/json'
local http = require 'http'
local shared = require 'shared'
local boundaries = require 'boundaries'
local drender = require 'default_render'
local ffi = require("ffi") 
ffi.cdef[[ 
  int getpid(void); 
]]

local time=0
function lovr.load()
  
end
function lovr.draw(pass)
  for i, func in ipairs(shared.conditioned_renderfunctions) do
    if func[3]==shared.data[func[2]] then
      func[1](pass)
    end
  end

end
function lovr.update(dt)
  if (os.clock()>time) then
    time=os.clock()+0.05
    pcall(function()
      status, webdata, headers = http.request("http://localhost:1469")
      shared.data=json.decode(webdata)
      if shared.data["datachange"] then
        status2, webdata2, headers2 = http.request("http://localhost:1469/position")
        shared.positioning=json.decode(webdata2)
      end
      if shared.data["requestpid"] then
        local pid=ffi.C.getpid()
        http.request("http://localhost:1469/pid/"..pid)
      end
    end)
  end
end