local renderhelp = {}
function renderhelp.get_p(x, y, z, a, ax, ay, az, dist)
    local s, c = math.sin(a), math.cos(a)
    -- This calculates the local -Z (forward) offset
    local dx = -ay * dist * s + ax * az * dist * (c - 1)
    local dy =  ax * dist * s + ay * az * dist * (c - 1)
    local dz = -dist * c + az * az * dist * (c - 1)
    return x + dx, y + dy, z + dz
end
return renderhelp