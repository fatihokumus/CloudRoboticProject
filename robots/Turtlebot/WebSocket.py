
from math import radians
import websocket
import json
import math
try:
    import thread
except ImportError:
    import _thread as thread
import time

isStarted = True
lastDegree = 0


def on_message(ws, message):
    global isStarted
    if message == "{\"message\": \"Orada misin?\"}":
        ws.send("{\"message\":\"Evet\"}")
        if isStarted == True:
            ws.send("{\"message\":\"Son Konumum: x:100; y:100\"}")
            isStarted = False
    elif "Rota" in message:
        thread.start_new_thread(routeorder, (ws, message))
    print(message)

def routeorder(ws,message):
    data = json.loads(message)
    points = json.loads(data["message"].replace("Rota:", ""))
    for i in range(len(points)-1):
        oldpoint = points[i]
        newpoint = points[i+1]
        x1 = newpoint[0]-oldpoint[0]
        y1= newpoint[1]-oldpoint[1]
        length = math.sqrt(x1*x1 + y1*y1)
        _radians = math.atan2(y1, x1)
        degrees = math.degrees(_radians)
        tempdegree = lastDegree + degrees
        lastDegree = degrees

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print("opened...")
    thread.start_new_thread(run, ())

def startwebsocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://10.42.0.231/robots/iot/M02R201/",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    thread.start_new_thread(startwebsocket)
    print("MERHAAABBAAA")
