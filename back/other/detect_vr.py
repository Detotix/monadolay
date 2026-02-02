import os
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import shared

monitoring_queue = {}
ignored_pids = set() 
vr_keywords = [b'openxr', b'DETECT_VR', b'vrclient', b'libovr', b'oculus', b'steamvr']
last_active_pids = {}
reignored_pids = set()


active_vr_indicators = [b'monado_shm', b'ValveIPCSHM', b'libxrizer.so',b'libopenxr_monado.so']

def is_vr_session_active(pid):
    try:
        with open(f'/proc/{pid}/maps', 'rb') as f:
            content = f.read()
            for indicator in active_vr_indicators:
                if indicator in content:
                    return True
    except:
        pass
    return False

def ignore_pid(pid):
    ignored_pids.add(pid)
    if pid in monitoring_queue:
        del monitoring_queue[pid]
    shared.shared_stored = [p for p in shared.shared_stored if str(p['pid']) != pid]
    reignored_pids.add(pid)

def update_vr_tracker(check_duration=15):

    global monitoring_queue, ignored_pids, last_active_pids
    
    now = time.time()
    current_pids = set()
    

    try:
        for entry in os.scandir('/proc'):
            if entry.is_dir() and entry.name.isdigit():
                current_pids.add(entry.name)
    except FileNotFoundError:
        return


    ignored_pids &= current_pids
    

    monitoring_pids = list(monitoring_queue.keys())
    try:
        for pid in monitoring_pids:
            if pid not in current_pids:
                del monitoring_queue[pid]
            else:
                if check_is_vr(pid):
                    register_vr_process(pid)
                    del monitoring_queue[pid]
                elif (now - monitoring_queue[pid]) > check_duration:
                    ignored_pids.add(pid)
                    del monitoring_queue[pid]
    except KeyError:
        print("[DETECT_VR] KeyError in monitoring queue.")

    known_active = set(last_active_pids.keys())
    new_pids = current_pids - known_active - ignored_pids - set(monitoring_queue.keys())
    
    for pid in new_pids:
        if check_is_vr(pid):
            register_vr_process(pid)
        else:
            monitoring_queue[pid] = now


    shared.shared_stored = [p for p in shared.shared_stored if str(p['pid']) in current_pids]
    last_active_pids = {str(p['pid']): p['name'] for p in shared.shared_stored}

def check_is_vr(pid):

    try:
        with open(f'/proc/{pid}/maps', 'rb') as f:
            content = f.read()
            return any(kw in content for kw in vr_keywords)
    except (PermissionError, FileNotFoundError, ProcessLookupError) as e:
        if e is ProcessLookupError:
            ignore_pid(pid)
            print(f"[DETECT_VR] Process {pid} throw process lookup error; ignoring.")
        return False

def register_vr_process(pid):

    try:
        with open(f'/proc/{pid}/comm', 'r') as f:
            name = f.read().strip()

        if not any(p['pid'] == int(pid) for p in shared.shared_stored):
            if name.lower() in shared.nameignore:
                ignore_pid(pid)
            if not pid in reignored_pids:
                print(f"[DETECT_VR] Registered VR process: {name} (PID: {pid})")
                shared.shared_stored.append({"name": name, "pid": int(pid)})
            else:
                print(f"[DETECT_VR] PID {pid} (name: {name}) was recently unregistered; skipping addition to shared_stored.")
            
    except:
        pass

