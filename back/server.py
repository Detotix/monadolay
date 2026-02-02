
import os
from json import dumps, loads
from logging import getLogger, WARNING
import other.detect_vr

from flask import Flask
from shared import shared, positioning


getLogger("werkzeug").setLevel(WARNING)


app = Flask(__name__)

@app.route('/')
def get_data():
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
    positioning.datachange=False
    return dumps(positioning.positions)

def run():
    app.run(port=1469)