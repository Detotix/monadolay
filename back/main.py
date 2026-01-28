from threading import Thread
from atexit import register as atexit_register
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from time import sleep, time
from sys import exit as sys_exit
from pathlib import Path
from psutil import process_iter, NoSuchProcess, AccessDenied
import pulsectl
import other.system
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
import gui
import other.system

def mute_click():
    if timing.last_mute_click <= time() and shared.systemkey_left:
        mic_muted=other.system.is_mic_muted()
        other.system.set_mic_mute(not mic_muted)
        shared.show_mute=not mic_muted
        timing.last_mute_click = time() + 0.20

def main():
    print(__file__)
    server_thread=Thread(target=server.run, daemon=True)
    server_thread.start()
    systemkey_thread=Thread(target=systemkey.main, daemon=True)
    systemkey_thread.start()
    gui_thread=Thread(target=gui.start_gui, daemon=True)
    gui_thread.start()
    while True:
        sleep(0.05)
        if shared.closed==True:
            break
        mute_click()
        #print(shared.systemkey_left,shared.systemkey_right)
        #print(tracemalloc.get_traced_memory())
    close()
    sys_exit()
    systemkey_thread.join()
    gui_thread.join()
    server_thread.join()

if __name__=="__main__":
    main()