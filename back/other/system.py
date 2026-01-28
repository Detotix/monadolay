import time
import pulsectl
from pydbus import SessionBus
from gi.repository import GLib

def pulsemute(mute):
    try:
        with pulsectl.Pulse('mic-control') as pulse:
            source = get_default_mic_source(pulse)
            if source:
                pulse.mute(source, mute)
                print(f"Fallback: Set mic mute to {mute} on device {source.description}")
    except Exception as e:
        print(f"Critical: Failed to set mic state via fallback: {e}")

        
def get_default_mic_source(pulse):
    server_info = pulse.server_info()
    default_name = server_info.default_source_name
    try:
        source = pulse.get_source_by_name(default_name)
        if source and not source.name.endswith(".monitor"):
            return source
    except:
        pass

    source_list = pulse.source_list()
    for source in source_list:
        if not source.name.endswith(".monitor"):
            return source
            

    return pulse.get_source_by_name(default_name)

def is_mic_muted():
    try:
        with pulsectl.Pulse('mic-check') as pulse:
            source = get_default_mic_source(pulse)
            if source:
                return bool(source.mute)
            return False
    except Exception as e:
        print(f"Error checking mic status: {e}")
        return False

def set_mic_mute(mute: bool):
    current_state = is_mic_muted()
    

    if current_state == mute:
        return

    kde_success = False

    try:

        bus = SessionBus()
        remote_object = bus.get(
            "org.kde.kglobalaccel", 
            "/component/kmix"
        )
        
        remote_object.invokeShortcut("mic_mute")
        time.sleep(0.15) 
        

        if is_mic_muted() != mute:

            remote_object.invokeShortcut("mic_mute")
        if is_mic_muted() != mute:
            pulsemute(mute)
            remote_object.invokeShortcut("mic_mute")
        if is_mic_muted() != mute:
            kde_success = False
        else:
            kde_success = True
        
    except (GLib.Error, Exception):

        kde_success = False


    if not kde_success:
        pulsemute(mute)
