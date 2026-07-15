import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add it to Python's import path
sys.path.insert(0, ROOT)

if not sys.argv[1]=="mainless":
    from main import main

import gui.release.control_panel as ctlpanel
from threading import Thread

def start_main():
    gui_thread=Thread(target=ctlpanel.start_gui, daemon=True)
    gui_thread.start()
    if not sys.argv[1]=="mainless":
        main()
    gui_thread.join()

if __name__=="__main__":
    start_main()