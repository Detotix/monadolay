import shared
import json
import pipe_sending
from shared import shared,change
import other.detect_vr
import other.monado_tasks
import os
import traceback 
PIPE_DEBUG=False

class monado_task:
    local_monado_task=other.monado_tasks.monado_task()
try:
    next(monado_task.local_monado_task)
except:
    shared.closed=True

#thread of reading the named pipe of lua
def read_pipe_thread():
    pipe_sending.pipe.lp_pipe=open("/tmp/monadolay_pipe_lp", "r")
    try:
        while not shared.closed:
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
                    if data["data_type"]=="monado_task":
                        monado_task_result=monado_task.local_monado_task.send({"name": data["data_value"][0], "info": None})
                        pipe_sending.pipe.send("monado_task_result", {"type": data["data_value"][0], "result":monado_task_result})
                        #if isinstance(monado_task_result, dict):
                        #    return dumps(monado_task_result)
                        #else:
                        #    return dumps({"result": monado_task_result})
                except:
                    pass
    except:
        shared.closed=True
        print("[PIPE PY] error in pipe thread, (monado was probably closed)")
    print("[ PIPE PY ] pipe ended")
