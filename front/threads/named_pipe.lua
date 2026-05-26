local thread = require "lovr.thread" 
local filesystem = require "lovr.filesystem" 
local timer = require "lovr.timer" 
local json = require "lib/json"

print("[ PIPE (LOVR) ] Waiting for writer...")

local file = nil


while not file do
    file = io.open("/tmp/monadolay_pipe_pl", "r")
    if not file then
        timer.sleep(0.1)
    end
end

print("[ PIPE (LOVR) ] Pipe opened, reading...")

local cont = true

while cont do
    local line = file:read("*l") 
    if line then
        if line == "close" then
            cont = false
        else
            local data = json.decode(line)
            print("[PIPE LUA] received data from python: " ..tostring(data.data_type) .. " = " .. tostring(data.data_value))
        end
    end
end

file:close()
