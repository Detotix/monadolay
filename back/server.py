
from json import dumps, loads
from logging import getLogger, WARNING

from flask import Flask
from shared import shared


getLogger("werkzeug").setLevel(WARNING)


app = Flask(__name__)

@app.route('/')
def hello_world():
    return dumps({"rendermode":shared.rendermode,"show_mute":shared.show_mute})

def run():
    app.run(port=1469)