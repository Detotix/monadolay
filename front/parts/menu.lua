local shared = require 'shared'
local renderhelp = require 'lib/renderhelp'
local menu = {}

function menu.rendercontroller(pass)
    local left_x, left_y, left_z, left_angle, left_ax, left_ay, left_az = lovr.headset.getPose("hand/left")
    local right_x, right_y, right_z, right_angle, right_ax, right_ay, right_az = lovr.headset.getPose("hand/right")
    pass:setColor(.255, .255, .255, 1)
    local lx, ly, lz = renderhelp.get_p(left_x, left_y, left_z, left_angle, left_ax, left_ay, left_az, -0.05)
    local rx, ry, rz = renderhelp.get_p(right_x, right_y, right_z, right_angle, right_ax, right_ay, right_az, -0.05)
    pass:text(shared.monado("battery_controller_left")["result"], lx, ly, lz, 0.2, left_angle, left_ax, left_ay, left_az, 0, "center", "middle")
    pass:text(shared.monado("battery_controller_right")["result"], rx, ry, rz, 0.2, right_angle, right_ax, right_ay, right_az, 0, "center", "middle")
    pass:setColor(.0, .0, .0, 0.6)
    x, y, z, angle, ax, ay, az = lovr.headset.getPose("head")
    pass:cube(x, y, z, 5, angle, ax, ay, az, "fill", 1, 1)
end
function menu.render(pass)
    menu.rendercontroller(pass)
end

return menu