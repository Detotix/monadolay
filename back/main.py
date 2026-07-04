
import os
import json
import presence

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

import sys


print(f"[MAIN] folder of installation : {Path(__file__).parent.parent}")
T_START=perf_counter()
DATA_FOLDER=f"{os.path.expanduser('~')}/.local/share/monadolay"



class close:
    #state
    closed=False

        
    #this is so it ignores errors that may accure while exiting    
    def _noerrorexit(exctype, value, traceback):
        pass

    #closes lovr on exit
    def close(a=None, b=None):
        if not close.closed:
            print(T_START)

            #turns off exeptions so it can close like intended
            sys.excepthook=close._noerrorexit
            
            #saves time played
            shared.saved_data["time_spend"]+=perf_counter()-T_START 
            with open(f"{DATA_FOLDER}/data.json", "w") as f:
                f.write(json.dumps(shared.saved_data))
            #closes lovr
            for proc in process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == 'lovr':
                        print(f"[MAIN] Killing LÖVR process PID {proc.pid}")
                        proc.terminate()
                except (NoSuchProcess, AccessDenied):
                    print("[MAIN] Couldn't find LÖVR process")

            #stops the discord presence
            presence.stop_presence()

            #deletes pipe files
            if os.path.exists("/tmp/monadolay_pipe_pl"): os.remove("/tmp/monadolay_pipe_pl")
            if os.path.exists("/tmp/monadolay_pipe_lp"): os.remove("/tmp/monadolay_pipe_lp")

            print("[MAIN] closing")
            shared.closed=True
            close.closed=True
            

#atexit_register(close)
signal(SIGQUIT, close.close)
signal(SIGINT, close.close)
signal(SIGTERM, close.close)



#import server
import systemkey

import other.system
def mute_click():
    mic_muted=other.system.is_mic_muted()
    if not systemkey.shared.systemkey_left[0] and shared.systemkey_left[1]: shared.systemkey_left[2]=True
    else: shared.systemkey_left[2]=False

    if shared.systemkey_left[2]:
        change.up("data", {"show_mute": not mic_muted})
        other.system.set_mic_mute(not mic_muted)

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

    #discord rich presence
    presence.discord_presence()

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
     
    #pipe.lp_pipe=open("/tmp/monadolay_pipe_lp", "r")
    pipe_sending.pipe.pl_pipe=open("/tmp/monadolay_pipe_pl", "w")
     
    #threads
    #server_thread=Thread(target=server.run, daemon=True)
    #server_thread.start()
    pipe_thread=Thread(target=named_pipe.read_pipe_thread, daemon=True)
    pipe_thread.start()
    systemkey_thread=Thread(target=systemkey.main, daemon=True)
    systemkey_thread.start()
     
    
    #gets current mute state
    change.up("data", {"show_mute": other.system.is_mic_muted()})
     
    #named_pipe.send_lua("show_mute",{"something":[shared.data["show_mute"]]})

    #checking if monado-service is running
    shared.monado_pid=other.detect_vr.is_running("monado-service")
    if not shared.monado_pid:
        print("[MAIN] monado-service process not found, closing")
        close.close()
    else:
        local_monado_task=monado_tasks.monado_task()
        next(local_monado_task)
    #initially turn on the overlay input

    local_monado_task.send({"name": "overlay_input_on", "info": None})
    
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
                close.close()
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
        if change.up("data")["rendermode"]:
            presence.stop_playing_game()

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
    close.close()
    sys_exit()
    systemkey_thread.join()
    gui_thread.join()
    #server_thread.join()
    pipe_thread.join()

if __name__=="__main__":
    main()