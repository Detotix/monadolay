class shared:
    vrloc=""
    closed=False
    lovrpid=None
    activeinstance=False
    monado_task=None
    nameignore=set(["envision", "steam.exe", "steam", "d3ddriverquery6", "xalia.exe"])
    data={"rendermode": True, "show_mute": False, "datachange": False, "requestpid": True}
    shared_stored = []
    renderswitch=False
    monado_pid=None
    t4=0
    systemkey_left=False
    systemkey_right=False
    unclicked_left=True
    unclicked_right=True
    render={"render":[]}
    settings={"openwindow": False}
class timing:
    last_mute_click=0
    last_menu_click=0

class positioning:
    positions={"mute": {"x":-0.3, "y":-0.17, "z":-0.5}}