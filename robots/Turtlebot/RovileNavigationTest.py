import rospy
from geometry_msgs.msg import Twist
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
points = []
ws = None

class DrawASquare():
    def __init__(self):
        global points
        global lastDegree
        global ws
        rospy.init_node('drawasquare', anonymous=False)

        rospy.on_shutdown(self.shutdown)

        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)

        r = rospy.Rate(5)
        turn_cmd = Twist()
        turn_cmd.linear.x = 0
        move_cmd = Twist()
        move_cmd.linear.x = 0.2

        x1 = 100
        y1 = 100
        kp = 0.3
        while 1==1:
            if points != []:
                for i in range(5):
                    degrees = 0
                    length = 0
                    if i == 0:
                        degrees = -29
                        length = 500
                    elif i == 1:
                        degrees = -120
                        length = 130
                    elif i == 2:
                        degrees = 78
                        length = 300
                    elif i == 3:
                        degrees = 66
                        length = 350
                    elif i == 4:
                        degrees = 66
                        length = 450

                    turn_cmd.angular.z = radians(float(degrees));

                    for x in range(0, 10):
                        self.cmd_vel.publish(turn_cmd)
                        r.sleep()

                    for x in range(0, int(length/8)):
                        self.cmd_vel.publish(move_cmd)
                        if i == 0:
                            x1 = x1 + int(x*kp*0.66)
                            y1 = y1 + int(x*kp*0.33)
                        elif i == 1:
                            x1 = x1 - int(x*kp * 1.8)
                        elif i == 2:
                            y1 = y1 + int(x*kp * 1.2)
                        elif i == 3:
                            x1 = x1 + int(x*kp*1.3)
                        elif i == 4:
                            y1 = y1 - int(x*kp*0.96)
                        ws.send("{\"message\":\"Son Konumum: x:" + str(x1) + "; y:" + str(y1) + "\"}")
                        r.sleep()
                    time.sleep(3)

                points = []
            time.sleep(1)


    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop Drawing Squares")
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)


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
    global points
    data = json.loads(message)
    points = json.loads(data["message"].replace("Rota:", ""))

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print("opened...")
    thread.start_new_thread(run, ())


def startwebsocket():
    global ws
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://10.42.0.231/robots/iot/M02R201/",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    thread.start_new_thread(startwebsocket, ())

    try:
        DrawASquare()
    except Exception as e:
        print(e)
