local thread = require "lovr.thread" 
local filesystem = require "lovr.filesystem" 
local timer = require "lovr.timer" 
local json = require "lib/json"

local channel = thread.getChannel('pipe_channel')


PIPE_DEBUG=false

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
            local ok, err pcall(function()
                local data = json.decode(line)
                channel:push(data)
                if PIPE_DEBUG then
                    print("[PIPE LUA] received data from python: " ..tostring(data.data_type) .. " = " .. tostring(line))
                end
                data = nil
                line=nil
            end)
            if err then
                print("[ PIPE (LOVR) ] Error decoding JSON: " .. err .. " | Line content: " .. tostring(line))
            end
        end
    end
end

file:close()
