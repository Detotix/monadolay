import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add it to Python's import path
sys.path.insert(0, ROOT)

from main import main
import gui.testing.dpg_gui as dpg_gui
from threading import Thread

def start_main():
    gui_thread=Thread(target=dpg_gui.start_gui, daemon=True)
    gui_thread.start()
    main()

if __name__=="__main__":
    start_main()