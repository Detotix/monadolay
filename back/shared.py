from pipe_sending import pipe
class shared:
    class direct_data:
        data={"rendermode": True, "show_mute": False, "datachange": False, "requestpid": True, "create_boundaries": False}
        render={"render":[]}
        settings={"openwindow": False}
        positions={"mute": {"x":-0.3, "y":-0.17, "z":-0.5}}
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
class change:
    #function to update or get the data

    
     def up(key, new_data=None):
        if new_data:
            current = getattr(shared.direct_data, key)
            merged = current | new_data
            setattr(shared.direct_data, key, merged)
            pipe.send(key, merged)
        return getattr(shared.direct_data, key)
