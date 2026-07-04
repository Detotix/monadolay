local http = require 'http'
local json = require 'lib/json'
local named_pipe = require 'lib/named_pipe'
local shared={}


shared.monado_results={}

shared.positioning={mute={x=-0.4, y=-0.17, z=-0.5}}
shared.settings={openwindow=false}
shared.render={render={}}
shared.data={rendermode=false, show_mute=false, datachange=false, create_boundaries=false}
shared.conditioned_renderfunctions={}
shared.localdata={}
shared.lp_pipe=nil
shared.renderfunctions={}
shared.localcolor={renderfull={.2, .2, .2, 1}}

function shared.monado(task)
    named_pipe.pipe_send("monado_task", {task})
    if shared.monado_results[task] then 
        return shared.monado_results[task]
    end
end

return shared