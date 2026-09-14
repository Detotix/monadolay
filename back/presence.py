from pipe_sending import pipe
from pypresence import Presence, PyPresenceException
from time import perf_counter
import shared

class current_presence:
    enabled=True
    rpc=None
    changetime=0
    playing=False

def playing_game(game_name):
    current_presence.playing=True
    pipe.send("proc_info", {"type":"GAME","name": game_name})

    if current_presence.enabled:
        try:
            current_presence.changetime=perf_counter()+40
            current_presence.rpc.update(
                state=f"Playing {game_name}",
                name="Monadolay",
                large_image="monadolay-playing",
                large_text="Monadolay - Overlay for Monado",
            )
        except:
            pass
def stop_playing_game():
    current_presence.playing=False
    pipe.send("proc_info", {"type":"NO_GAME"})

    if current_presence.changetime<perf_counter() and current_presence.enabled:
        try:
            current_presence.rpc.update(
                state="No game running",
                name="Monadolay",
                large_image="monadolay",
                large_text="Monadolay - Overlay for Monado",
            )
        except:
            pass
def stop_presence():
    if current_presence.enabled:
        print("[PRESENCE] closing")
        current_presence.rpc.clear()
        current_presence.rpc.close()
def discord_presence():
    current_presence.enabled=shared.shared.saved_data["discord_presence"]
    if current_presence.enabled:
        try:
            client_id = "1517909906345295974"
            RPC = Presence(client_id)
            RPC.connect()
            current_presence.rpc=RPC
            stop_playing_game()
        except PyPresenceException:
            current_presence.enabled=False
            print("[PRESENCE] Discord is not open (disabling the presence!)")
    else:
        print("[PRESENCE] (DISABLED)")
