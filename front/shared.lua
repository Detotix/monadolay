local http = require 'http'
local json = require 'lib/json'
local shared={}

function shared.monado(task)
    webres={}
    pcall(function()
        local status, webdata, headers = http.request("http://localhost:1469/monado/"..task)
        webres = json.decode(webdata)
    end)
    return webres
end

shared.positioning={mute={x=-0.4, y=-0.17, z=-0.5}}
shared.settings={openwindow=false}
shared.render={render={}}
shared.data={rendermode=false, show_mute=false, datachange=false, create_boundaries=false}
shared.conditioned_renderfunctions={}
shared.localdata={}
shared.renderfunctions={}
shared.localcolor={renderfull={.2, .2, .2, 1}}
return shared