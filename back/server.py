
import os
from json import dumps, loads
from logging import getLogger, WARNING
import other.detect_vr
import other.monado_tasks
from flask import Flask
from shared import shared, positioning
import other.monado_tasks

getLogger("werkzeug").setLevel(WARNING)


app = Flask(__name__)
class monado_task:
    local_monado_task=other.monado_tasks.monado_task()
next(monado_task.local_monado_task)
@app.route('/')
def get_data():
    if shared.renderswitch:
        shared.data["rendermode"]=False
    return dumps(shared.data)
@app.route('/pid/<int:pid>')
def get_pid(pid):
    shared.data["requestpid"] = False
    shared.lovrpid=pid
    other.detect_vr.ignore_pid(str(pid))
    other.detect_vr.ignore_pid(str(os.getpid()))
    return "ok"

@app.route('/position')
def get_position():
    return dumps(positioning.positions)
@app.route('/render')
def get_render():
    return dumps(shared.render)
@app.route('/settings')
def get_settings():
    positioning.datachange=False
    return dumps(shared.settings)
@app.route('/monado/<task>')
def get_monado_task(task):
    monado_task_result=monado_task.local_monado_task.send({"name": task, "info": None})
    if isinstance(monado_task_result, dict):
        return dumps(monado_task_result)
    else:
        return dumps({"result": monado_task_result})
def run():
    app.run(port=1469)