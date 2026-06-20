from pypresence import Presence
from time import perf_counter
import shared

class current_presence:
    rpc=None
    changetime=0


def playing_game(game_name):
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
    try:
        if current_presence.changetime>perf_counter():
            return
        current_presence.rpc.update(
            state="No game running",
            name="Monadolay",
            large_image="monadolay",
            large_text="Monadolay - Overlay for Monado",
        )
    except:
        pass

def discord_presence():

    client_id = "1517909906345295974"
    RPC = Presence(client_id)
    RPC.connect() 
    current_presence.rpc=RPC
    stop_playing_game()
