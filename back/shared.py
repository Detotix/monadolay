from pipe_sending import pipe

#hooks are there so u can execute code on data changes without changing code allover the program
class hooks:
    direct_data_hooks={}
class shared:
    class direct_data:
        data={"rendermode": True, "show_mute": False, "datachange": False, "requestpid": True, "create_boundaries": False, "launch": False, "launching_game":"None"}
        render={"render":[]}
        settings={"openwindow": False}
        positions={"mute": {"x":-0.3, "y":-0.17, "z":-0.5}}
    vrloc=""
    closed=False
    lovrpid=None
    activeinstance=False
    monado_task=None
    nameignore=set(["envision", "steam.exe", "steam", "d3ddriverquery6", "xalia.exe", "winedevice", "winedevice.exe", "explorer", "explorer.exe", "envision", "xalia.exe", "steam.exe", "vrcx-0", "x86_64-linux-gn", "steam", "vrstartup", "vrcompositor", "Main", "chromedriver.ex", "conhost.exe",])
    shared_stored = []
    saved_data = {}
    renderswitch=False
    rendermodechange=False
    monado_pid=None
    t4=0
    systemkey_left=[False,False,False]
    systemkey_right=[False,False,False]
class change:
    # for changing data or getting it from direct_data block with sync to lua
    # example:
    # change.up("data", {"show_mute": other.system.is_mic_muted()}) *other.system.is_mic_muted() returns true or false
    # key = thing to modify, new_data = data that should get merged update = if no data provided but should sync to lua anyway
    def up(key, new_data=None, update=False):
        #code for actually changing stuff
        if new_data or update:
            current = getattr(shared.direct_data, key)
            try:
                merged = current | new_data
                setattr(shared.direct_data, key, merged)
                pipe.send(key, merged)
            except:
                pipe.send(key, current)
            #code for hooks
            if key in hooks.direct_data_hooks:
                for i, a in enumerate(hooks.direct_data_hooks[key]):
                    a(new_data,current,merged)
        return getattr(shared.direct_data, key)
    def new_hook(key, hook):
        if key in hooks.direct_data_hooks:
            hooks.direct_data_hooks[key].append(hook)
        else:
            hooks.direct_data_hooks[key]=[hook]
