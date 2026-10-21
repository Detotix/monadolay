from shared import change
def exiting_game(new_data, current, merged):
    print(" new:"+str(new_data)+"\n current:",str(current)+"\n merged:",str(merged))

def init_hooks():
    change.new_hook("data", exiting_game)
