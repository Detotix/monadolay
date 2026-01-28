local json = require 'lib/json'
local http = require 'http'
local shared = require 'shared'

local time=0
local h1={}
local h2={}

function lovr.load()
end
function lovr.draw(pass)
  if (os.clock()>time) then
    time=os.clock()+0.005
    pcall(function()
      status, webdata, headers = http.request("http://localhost:1469")
      shared.data=json.decode(webdata)
      if shared.data["datachange"] then
        status2, webdata2, headers2 = http.request("http://localhost:1469/position")
        shared.positioning=json.decode(webdata2)
      end
    end)
  end
  --pass:setColor(.1, .1, .12)
  --pass:plane(0, 0, 0, 100, 100, -math.pi / 2, 1, 0, 0)
  if shared.data["rendermode"] then
    pass:setColor(.2, .2, .2)          
    pass:plane(0, -0.09, 0, 100, 100, -math.pi / 2, 1, 0, 0, 'line', 100, 100)
    pass:setColor(.0, .255, .0)  
    h1.x, h1.y, h1.z = lovr.headset.getPosition("hand/left")
    
    h2.x, h2.y, h2.z = lovr.headset.getPosition("hand/right")
    pass:sphere(h1.x,h1.y,h1.z, 0.05, 0, 0, 1, 0, 48, 24)
    pass:setColor(.255, .0, .0)  
    pass:sphere(h2.x,h2.y,h2.z, 0.05, 0, 0, 1, 0, 48, 24)
  end
  if shared.data["show_mute"] then
    angle, ax, ay, az = lovr.headset.getOrientation()
    x, y, z = lovr.headset.getPosition()

    local offset_x, offset_y, offset_z = shared.positioning["mute"]["x"], shared.positioning["mute"]["y"], shared.positioning["mute"]["z"]
    local quat = {ax, ay, az, math.cos(angle/2)}
    local cos_a = math.cos(angle / 2)
    local sin_a = math.sin(angle / 2)
    local qx, qy, qz, qw = ax * sin_a, ay * sin_a, az * sin_a, cos_a
    local rotated_x = (1 - 2*qy*qy - 2*qz*qz) * offset_x + (2*qx*qy - 2*qz*qw) * offset_y + (2*qx*qz + 2*qy*qw) * offset_z
    local rotated_y = (2*qx*qy + 2*qz*qw) * offset_x + (1 - 2*qx*qx - 2*qz*qz) * offset_y + (2*qy*qz - 2*qx*qw) * offset_z
    local rotated_z = (2*qx*qz - 2*qy*qw) * offset_x + (2*qy*qz + 2*qx*qw) * offset_y + (1 - 2*qx*qx - 2*qy*qy) * offset_z
    local sphere_x = x + rotated_x
    local sphere_y = y + rotated_y
    local sphere_z = z + rotated_z  
    pass:setColor(.255, .10, .10)
    pass:sphere(sphere_x, sphere_y, sphere_z, 0.02, 0, 0, 1, 0, 48, 24)
  end
end
function lovr.update(dt)
  --for i, hand in ipairs(lovr.headset.getHands()) do
  --  print(hand, lovr.headset.getPose(hand))
  --end

end