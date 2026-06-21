import shared
import json
import pipe_sending
from shared import shared,change
import other.detect_vr
import os

PIPE_DEBUG=False
#thread of reading the named pipe of lua
def read_pipe_thread():
    pipe_sending.pipe.lp_pipe=open("/tmp/monadolay_pipe_lp", "r")
    try:
        for line in pipe_sending.pipe.lp_pipe:
            
            if line.strip()=="close":
                pipe_sending.pipe.close_pipe()
                print("[PIPE PY] received close command, closing")
                shared.closed=True
                break
            else:
                if PIPE_DEBUG: print(f"[PIPE PY] received data from lua: {line.strip()}")
            try:
               data=json.loads(line.strip())
               if data["data_type"]=="pid":
                pid=data["data_value"][0]
                change.up("data", {"requestpid": False})
                shared.lovrpid=pid
                other.detect_vr.ignore_pid(str(pid))
                other.detect_vr.ignore_pid(str(os.getpid()))
            except:
                pass
    except:
        shared.closed=True
        print("[PIPE PY] error in pipe thread, (monado was probably closed)")
