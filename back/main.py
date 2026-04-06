import os
from threading import Thread
from atexit import register as atexit_register
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from time import sleep, time
from sys import exit as sys_exit
from pathlib import Path
from psutil import process_iter, NoSuchProcess, AccessDenied
import other.detect_vr
import other.system
import other.monado_tasks as monado_tasks
#import tracemalloc 
#tracemalloc.start()

from shared import shared, timing

shared.vrloc=Path(__file__).parent.parent

print(Path(__file__).parent.parent)


def close(a=None, b=None):
    for proc in process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'lovr':
                print(f"[MAIN] Killing LÖVR process PID {proc.pid}")
                proc.terminate()
        except (NoSuchProcess, AccessDenied):
            print("[MAIN] Couldn't find LÖVR process")
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
    if not shared.systemkey_left and shared.unclicked_left:
        shared.unclicked_left=False

    if timing.last_mute_click <= time() and shared.systemkey_left and not shared.unclicked_left:
        mic_muted=other.system.is_mic_muted()
        other.system.set_mic_mute(not mic_muted)
        shared.data["show_mute"]=not mic_muted
        timing.last_mute_click = time() + 0.01
        shared.unclicked_left=True

def menu_click():
    if not shared.systemkey_right and shared.unclicked_right:
        shared.unclicked_right=False
    
    if timing.last_menu_click <= time() and shared.systemkey_right and not shared.unclicked_right:
        #toggle menu
        if "menu" in shared.render["render"]: shared.render["render"].remove("menu")
        else: shared.render["render"].append("menu")
        
        shared.data["datachange"]=True
        timing.last_menu_click = time() + 0.01
        shared.unclicked_right=True
def main():

    shared.data["show_mute"]=other.system.is_mic_muted()

    server_thread=Thread(target=server.run, daemon=True)
    server_thread.start()
    systemkey_thread=Thread(target=systemkey.main, daemon=True)
    systemkey_thread.start()
    shared.monado_pid=other.detect_vr.is_running("monado-service")
    if not shared.monado_pid:
        shared.closed=True
        print("[MAIN] monado-service process not found, closing")
    else:
        local_monado_task=monado_tasks.monado_task()
        next(local_monado_task)
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
            shared.data["rendermode"]=False
        else:
            foundactive=False
            for i, process in enumerate(shared.shared_stored):
                if other.detect_vr.is_vr_session_active(str(process['pid'])):
                    foundactive=True
                    break
            shared.activeinstance=foundactive
            shared.data["rendermode"]=not foundactive
        if shared.closed:
            break

        #this part is for mute
        mute_click()
        #this part is for opening the menu
        menu_click()
        #print(shared.systemkey_left,shared.systemkey_right)
        #print(tracemalloc.get_traced_memory())
    close()
    sys_exit()
    systemkey_thread.join()
    gui_thread.join()
    server_thread.join()

if __name__=="__main__":
    main()