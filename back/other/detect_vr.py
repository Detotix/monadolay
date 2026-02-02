import os
import time
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import shared

# Constants for optimization
CHECK_DURATION = 15
MAPS_READ_SIZE = 8192  # Read first 8KB instead of entire file - maps starts with mapped regions
CACHE_TTL = 0.5  # Cache VR status for 0.5 seconds

# Pre-compile bytes for faster comparison
vr_keywords = (b'openxr', b'DETECT_VR', b'vrclient', b'libovr', b'oculus', b'steamvr')
active_vr_indicators = (b'monado_shm', b'ValveIPCSHM', b'libxrizer.so', b'libopenxr_monado.so')

# Module-level state for caching
ignored_pids = set()
monitoring_queue = {}
last_active_pids = {}
reignored_pids = set()
vr_status_cache = {}  # pid -> (timestamp, is_vr)
process_vr_cache = {}  # pid -> (timestamp, is_active)

def is_cached_valid(cache_dict, pid, ttl=CACHE_TTL):
    """Check if cached value is still valid."""
    if pid in cache_dict:
        timestamp, value = cache_dict[pid]
        if time.time() - timestamp < ttl:
            return True, value
    return False, None

def set_cache(cache_dict, pid, value):
    """Set cached value with current timestamp."""
    cache_dict[pid] = (time.time(), value)

def is_vr_session_active(pid):
    """Check if PID has active VR session with caching."""
    pid_str = str(pid)
    valid, cached = is_cached_valid(process_vr_cache, pid_str)
    if valid:
        return cached
    
    try:
        # Use buffered reading - only read first 8KB where shared mem mappings typically are
        with open(f'/proc/{pid}/maps', 'rb') as f:
            content = f.read(MAPS_READ_SIZE)
            for indicator in active_vr_indicators:
                if indicator in content:
                    set_cache(process_vr_cache, pid_str, True)
                    return True
    except:
        pass
    set_cache(process_vr_cache, pid_str, False)
    return False

def ignore_pid(pid):
    """Add PID to ignore list and clean up associated data."""
    ignored_pids.add(pid)
    if pid in monitoring_queue:
        del monitoring_queue[pid]
    if pid in vr_status_cache:
        del vr_status_cache[pid]
    shared.shared_stored = [p for p in shared.shared_stored if str(p['pid']) != pid]
    reignored_pids.add(pid)

def update_vr_tracker():
    """Optimized VR process tracker with minimal I/O operations."""
    global last_active_pids
    
    now = time.time()
    current_pids = set()
    
    # Get current PIDs efficiently
    try:
        for entry in os.scandir('/proc'):
            if entry.name.isdigit():
                current_pids.add(entry.name)
    except FileNotFoundError:
        return
    
    # Clean up ignored PIDs that no longer exist
    ignored_pids.intersection_update(current_pids)
    
    # Clean up expired cache entries
    expired = [pid for pid, (ts, _) in vr_status_cache.items() if now - ts > CACHE_TTL]
    for pid in expired:
        del vr_status_cache[pid]
    
    # Process monitoring queue
    monitoring_pids = list(monitoring_queue.keys())
    for pid in monitoring_pids:
        if pid not in current_pids:
            del monitoring_queue[pid]
            continue
        
        # Check cache first
        valid, is_vr = is_cached_valid(vr_status_cache, pid)
        if not valid:
            is_vr = fast_check_is_vr(pid)
            set_cache(vr_status_cache, pid, is_vr)
        try:
            if is_vr:
                register_vr_process(pid)
                del monitoring_queue[pid]
            elif (now - monitoring_queue[pid]) > CHECK_DURATION:
                ignored_pids.add(pid)
                del monitoring_queue[pid]
        except KeyError:
            print("[DETECT_VR] KeyError in monitoring queue.")
    # Process new PIDs efficiently
    known_active = set(last_active_pids.keys())
    monitored_and_ignored = ignored_pids | set(monitoring_queue.keys())
    new_pids = current_pids - known_active - monitored_and_ignored
    
    for pid in new_pids:
        # Quick check with cache
        valid, is_vr = is_cached_valid(vr_status_cache, pid)
        if not valid:
            is_vr = fast_check_is_vr(pid)
            set_cache(vr_status_cache, pid, is_vr)
        
        if is_vr:
            register_vr_process(pid)
        else:
            monitoring_queue[pid] = now
    
    # Cleanup shared_stored - use set for O(1) lookup
    current_pids_int = {int(p) for p in current_pids}
    shared.shared_stored = [p for p in shared.shared_stored if p['pid'] in current_pids_int]
    last_active_pids = {str(p['pid']): p['name'] for p in shared.shared_stored}

def fast_check_is_vr(pid):
    """Fast VR check with buffered reading and early exit."""
    try:
        with open(f'/proc/{pid}/maps', 'rb') as f:
            # Read in chunks to avoid loading entire file
            content = f.read(MAPS_READ_SIZE)
            for kw in vr_keywords:
                if kw in content:
                    return True
            # If not found in first chunk, check if file is larger
            while len(content) == MAPS_READ_SIZE:
                content = f.read(MAPS_READ_SIZE)
                for kw in vr_keywords:
                    if kw in content:
                        return True
    except (PermissionError, FileNotFoundError, ProcessLookupError):
        if sys.exc_info()[0] is ProcessLookupError:
            ignore_pid(pid)
    return False

def check_is_vr(pid):
    """Public VR check with caching."""
    valid, result = is_cached_valid(vr_status_cache, str(pid))
    if valid:
        return result
    try:
        with open(f'/proc/{pid}/maps', 'rb') as f:
            content = f.read()
            result = any(kw in content for kw in vr_keywords)
            set_cache(vr_status_cache, str(pid), result)
            return result
    except (PermissionError, FileNotFoundError, ProcessLookupError) as e:
        if isinstance(e, ProcessLookupError):
            ignore_pid(pid)
            print(f"[DETECT_VR] Process {pid} throw process lookup error; ignoring.")
        return False

def register_vr_process(pid):
    """Register a VR process with duplicate checking."""
    try:
        with open(f'/proc/{pid}/comm', 'r') as f:
            name = f.read().strip()

        if not any(p['pid'] == int(pid) for p in shared.shared_stored):
            if name.lower() in shared.nameignore:
                ignore_pid(pid)
                return
            if pid not in reignored_pids:
                print(f"[DETECT_VR] Registered VR process: {name} (PID: {pid})")
                shared.shared_stored.append({"name": name, "pid": int(pid)})
            else:
                print(f"[DETECT_VR] PID {pid} (name: {name}) was recently unregistered; skipping addition to shared_stored.")
    except:
        pass
