import json
class pipe:
    pl_pipe=None
    def close_pipe():
        pipe.pl_pipe.write("close\n")
        pipe.pl_pipe.flush()
    def send(data_type, data_value):
        pipe.pl_pipe.write(json.dumps({"data_type": data_type, "data_value": data_value}) + "\n")
        pipe.pl_pipe.flush()