
class shared:
    data={"rendermode": True, "show_mute": False, "datachange": False, "requestpid": True}        
    vrloc=""
    closed=False
    lovrpid=None
    activeinstance=False
    monado_task=None
    nameignore=set(["envision", "steam.exe", "steam", "d3ddriverquery6", "xalia.exe"])
    shared_stored = []
    saved_data = {}
    renderswitch=False
    rendermodechange=False
    monado_pid=None
    t4=0
    systemkey_left=[False,False,False]
    systemkey_right=[False,False,False]
    render={"render":[]}
    settings={"openwindow": False}
class pipe:
    pl_pipe=None
class positioning:
    positions={"mute": {"x":-0.3, "y":-0.17, "z":-0.5}}