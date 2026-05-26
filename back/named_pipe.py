import shared
import json


class update:
    def settings():
        shared.positioning.datachange=False
        send_lua("settings", shared.settings)
    def render():
        send_lua("render", shared.render)
    def data():
        send_lua("data", shared.data)

#thread of reading the named pipe of lua
def read_pipe_thread():
    shared.pipe.lp_pipe=open("/tmp/monadolay_pipe_lp", "r")
    try:
        for line in shared.pipe.lp_pipe:
            
            if line.strip()=="close":
                close_pipe()
                print("[PIPE PY] received close command, closing")
                shared.closed=True
                break
            else:
                print(f"[PIPE PY] received data from lua: {line.strip()}")
    except:
        shared.closed=True
        print("[PIPE PY] error in pipe thread, (monado was probably closed)")
