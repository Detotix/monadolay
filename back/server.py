
from json import dumps, loads
from logging import getLogger, WARNING

from flask import Flask
from shared import shared, positioning


getLogger("werkzeug").setLevel(WARNING)


app = Flask(__name__)

@app.route('/')
def get_data():
    return dumps({"rendermode":shared.rendermode,"show_mute":shared.show_mute, "datachange":positioning.datachange})
@app.route('/position')
def get_position():
    positioning.datachange=False
    return dumps(positioning.positions)

def run():
    app.run(port=1469)