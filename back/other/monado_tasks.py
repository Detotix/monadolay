from libmonado_bindings import Monado, DeviceRole
import other.detect_vr
import shared

def _clients(monado, info):
    return monado.clients()

def _update_vr_tracker(monado, info):
    primary_client=False
    for client in monado.clients():
        if client.is_primary():
            primary_client=True
    if not primary_client:
        print("[MONADO_TASK] No primary client found")
        other.detect_vr.update_vr_tracker()
    return None
def monado_task():
    
    tasks={"clients": _clients,"update_vr_tracker": _update_vr_tracker}
    result=None

    with Monado.auto_connect() as monado:
        print("[MONADO_TASK] Connected to Monado")
        while True:
            task = yield result
            if task["name"] in tasks:
                result = tasks[task["name"]](monado, task["info"])
