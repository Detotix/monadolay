from libmonado_bindings import Monado, DeviceRole
import other.detect_vr
from shared import change, shared

def _battery_controller_left(monado, info):
    try:return int(monado.device_from_role(DeviceRole.LEFT).battery_status().charge*100)
    except:return None
def _battery_controller_right(monado, info):
    try:return int(monado.device_from_role(DeviceRole.RIGHT).battery_status().charge*100)
    except:return None
def _overlay_input_on(monado, info):
    for client in monado.clients():
        if client.is_overlay():
            client.set_io_active(False)
        else:
            client.set_io_active(True)
        if change.up("data")["rendermode"] or client.name()=="monadolay_headless_instance": client.set_io_active(True)
def _overlay_input_off(monado, info):
    for client in monado.clients():
        if client.is_overlay():
            client.set_io_active(True)
        else:
            client.set_io_active(False)
        if change.up("data")["rendermode"] or client.name()=="monadolay_headless_instance": client.set_io_active(True)
def _update_vr_tracker(monado, info):
    primary_client=False
    for client in monado.clients():
        if client.is_primary():
            primary_client=True
    if not primary_client:
        print("[MONADO_TASK] No primary client found")
        other.detect_vr.update_vr_tracker()
        shared.activeinstance=False
    return None
def monado_task():
    
    tasks={"overlay_input_on": _overlay_input_on, "overlay_input_off": _overlay_input_off, "update_vr_tracker": _update_vr_tracker, "battery_controller_left": _battery_controller_left, "battery_controller_right": _battery_controller_right}
    result=None
    try:
        with Monado.auto_connect() as monado:
            print("[MONADO_TASK] Connected to Monado")
            while True:
                try:
                    task = yield result
                    if task["name"] in tasks:
                        result = tasks[task["name"]](monado, task["info"])
                except Exception as e:
                    if not e==RuntimeError:
                        print("[MONADO_TASK] Monado was probably closeds (exiting)")
                        shared.closed=True
                        break
                    print("[MONADO_TASK] Error in task execution")
                    print(f"[MONADO_TASK] Task: {task}")
    except:
        shared.closed=True