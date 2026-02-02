class shared:
    systemkey_left=False
    systemkey_right=False
    vrloc=""
    closed=False
    lovrpid=None
    activeinstance=False
    nameignore=set(["envision", "steam.exe", "steam", "d3ddriverquery6"])
    data={"rendermode": True, "show_mute": False, "datachange": False, "requestpid": True}
    shared_stored = []
class timing:
    last_mute_click=0


class positioning:
    positions={"mute": {"x":-0.3, "y":-0.27, "z":-0.5}}