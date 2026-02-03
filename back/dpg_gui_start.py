from main import main
import dpg_gui as dpg_gui
from threading import Thread

def start_main():
    gui_thread=Thread(target=dpg_gui.start_gui, daemon=True)
    gui_thread.start()
    main()

if __name__=="__main__":
    start_main()