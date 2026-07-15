import ctypes
import queue
import threading

q = queue.Queue()


lib = ctypes.CDLL("./controlpanel.so") 


CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

def py_callback(data):
    
    q.put(data.decode('utf-8'))


cb = CALLBACK(py_callback)

def start_gui():

    worker_thread = threading.Thread(target=lib.start_worker, args=(cb,), daemon=True)

    worker_thread.start()

    
    print("Python GUI-Reader gestartet... Warte auf Events von X11!")
    while True:
        try:
            msg = q.get(timeout=1.0)
            print("Python erhielt:", msg)
        except queue.Empty:
            continue