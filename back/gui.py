from dearpygui.dearpygui import window, add_button, create_context, create_viewport, setup_dearpygui, show_viewport, is_dearpygui_running, render_dearpygui_frame, destroy_context
from shared import shared
import other.system

def change_rendermode():
    shared.rendermode=not shared.rendermode
    print("[GUI] changed rendermode")

def change_showmute():
    mic_muted=other.system.is_mic_muted()
    print("[GUI]", mic_muted)
    other.system.set_mic_mute(not mic_muted)
    shared.show_mute=not mic_muted
    print("[GUI] changed show_mute")

def open_devoptions():
    with window(label="dev", no_close=False):
        add_button(label="rendermodetoggle",callback=change_rendermode)
        add_button(label="toggle_mute",callback=change_showmute)
    
def start_gui():
    create_context()
    create_viewport(title='monadolay vr', width=600, height=300)    
    with window(label="vr", no_close=True):
        add_button(label="open devtools",callback=open_devoptions)

    setup_dearpygui()
    show_viewport()
    while is_dearpygui_running():
        render_dearpygui_frame()

    destroy_context()
    shared.closed=True
