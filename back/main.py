
import os
import json

from threading import Thread
from atexit import register as atexit_register
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from time import sleep, time, perf_counter
from sys import exit as sys_exit
from pathlib import Path
from psutil import process_iter, NoSuchProcess, AccessDenied
import named_pipe
import other.detect_vr
import other.system
import other.monado_tasks as monado_tasks
import pipe_sending
#import tracemalloc 
#tracemalloc.start()

from shared import shared, pipe, change

shared.vrloc=Path(__file__).parent.parent

print(Path(__file__).parent.parent)
T_START=perf_counter()
DATA_FOLDER=f"{os.path.expanduser('~')}/.local/share/monadolay"

#closes lovr on exit
def close(a=None, b=None):
    print(T_START)
    shared.saved_data["time_spend"]+=perf_counter()-T_START 
    with open(f"{DATA_FOLDER}/data.json", "w") as f:
        f.write(json.dumps(shared.saved_data))
    for proc in process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'lovr':
                print(f"[MAIN] Killing LÖVR process PID {proc.pid}")
                proc.terminate()
        except (NoSuchProcess, AccessDenied):
            print("[MAIN] Couldn't find LÖVR process")
    os.remove("/tmp/monadolay_pipe_pl")
    os.remove("/tmp/monadolay_pipe_lp")
    print("[MAIN] closing")
    shared.closed=True

#atexit_register(close)
signal(SIGQUIT, close)
signal(SIGINT, close)
signal(SIGTERM, close)



import server
import systemkey

import other.system
def mute_click():
    if not systemkey.shared.systemkey_left[0] and shared.systemkey_left[1]: shared.systemkey_left[2]=True
    else: shared.systemkey_left[2]=False

    if shared.systemkey_left[2]:
        mic_muted=other.system.is_mic_muted()
        other.system.set_mic_mute(not mic_muted)
        change.up("data", {"show_mute": not mic_muted})

    shared.systemkey_left[1]=shared.systemkey_left[0]

def menu_click(local_monado_task):
    if not systemkey.shared.systemkey_right[0] and shared.systemkey_right[1]: shared.systemkey_right[2]=True
    else: shared.systemkey_right[2]=False
    if shared.systemkey_right[2]:
        #toggle menu
        if "menu" in change.up("render")["render"]: 
            shared.direct_data.render["render"].remove("menu")
            change.up("render", {})
            local_monado_task.send({"name": "overlay_input_on", "info": None})
        else: 
            shared.direct_data.render["render"].append("menu")
            change.up("render", {})
            local_monado_task.send({"name": "overlay_input_off", "info": None})
        
        change.up("data", {"datachange": True})
    shared.systemkey_right[1]=shared.systemkey_right[0]
def main():

    #initial data folder check
    if not os.path.exists(DATA_FOLDER) or not os.path.exists(f"{DATA_FOLDER}/data.json"):
        os.makedirs(DATA_FOLDER,exist_ok=True)
        with open(f"{DATA_FOLDER}/data.json", "w") as f:
            f.write(json.dumps({"time_spend":0}))
    with open(f"{DATA_FOLDER}/data.json", "r") as f:
        shared.saved_data=json.load(f)
    #creates named pipes if they dont exist
    if not os.path.exists("/tmp/monadolay_pipe_pl"): os.mkfifo("/tmp/monadolay_pipe_pl")
    if not os.path.exists("/tmp/monadolay_pipe_lp"): os.mkfifo("/tmp/monadolay_pipe_lp")
    print("ok")
    #pipe.lp_pipe=open("/tmp/monadolay_pipe_lp", "r")
    pipe_sending.pipe.pl_pipe=open("/tmp/monadolay_pipe_pl", "w")
    print("ok")
    #threads
    server_thread=Thread(target=server.run, daemon=True)
    server_thread.start()
    pipe_thread=Thread(target=named_pipe.read_pipe_thread, daemon=True)
    pipe_thread.start()
    systemkey_thread=Thread(target=systemkey.main, daemon=True)
    systemkey_thread.start()
    print("ok")
    
    #gets current mute state
    change.up("data", {"show_mute": other.system.is_mic_muted()})
    print("ok")
    #named_pipe.send_lua("show_mute",{"something":[shared.data["show_mute"]]})

    #checking if monado-service is running
    shared.monado_pid=other.detect_vr.is_running("monado-service")
    if not shared.monado_pid:
        shared.closed=True
        print("[MAIN] monado-service process not found, closing")
    else:
        local_monado_task=monado_tasks.monado_task()
        next(local_monado_task)
    #initially turn on the overlay input
    print("ok")
    local_monado_task.send({"name": "overlay_input_on", "info": None})
    print("ok")
    
    #main loop
    while True:
        sleep(0.05)
        shared.t4+=1
        #snapshot = tracemalloc.take_snapshot() 
        #top_stats = snapshot.statistics("lineno") 
        #for stat in top_stats[:20]: print(stat)
        #print("-----"*5)
        if shared.t4==4:
            shared.t4=0
            if not os.path.exists(f"/proc/{shared.monado_pid}"):
                shared.closed=True
                print("[MAIN] monado-service process ended, closing")
            if not shared.activeinstance:
                other.detect_vr.update_vr_tracker()
            else:
                local_monado_task.send({"name": "update_vr_tracker", "info": None})

        if (shared.shared_stored and shared.activeinstance):
            shared.activeinstance=True
            if change.up("data")["rendermode"]:
                change.up("data", {"rendermode": False})
        else:
            foundactive=False
            for i, process in enumerate(shared.shared_stored):
                if other.detect_vr.is_vr_session_active(str(process['pid'])):
                    foundactive=True
                    break
            shared.activeinstance=foundactive
            if change.up("data")["rendermode"]!=foundactive:
                change.up("data", {"rendermode": not foundactive})
        if shared.closed:
            break

        #this part is for mute
        mute_click()
        #this part is for opening the menu
        menu_click(local_monado_task)
        #print(shared.systemkey_left,shared.systemkey_right)
        #print(tracemalloc.get_traced_memory())

        if shared.rendermodechange!=change.up("data")["rendermode"]:
            shared.rendermodechange=change.up("data")["rendermode"]
            if change.up("data")["rendermode"]:local_monado_task.send({"name": "overlay_input_off", "info": None})
            else:                        local_monado_task.send({"name": "overlay_input_on", "info": None})
    #closing
    close()
    sys_exit()
    systemkey_thread.join()
    gui_thread.join()
    server_thread.join()
    pipe_thread.join()

if __name__=="__main__":
    main()