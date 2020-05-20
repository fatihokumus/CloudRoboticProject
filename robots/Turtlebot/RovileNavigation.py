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

class DrawASquare():
    def __init__(self):
        global points
        global lastDegree
        rospy.init_node('drawasquare', anonymous=False)

        rospy.on_shutdown(self.shutdown)

        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)

        r = rospy.Rate(5);
        while 1==1:
            if points != []:
                for i in range(len(points) - 1):
                    oldpoint = points[i]
                    newpoint = points[i + 1]
                    x1 = newpoint[0] - oldpoint[0]
                    y1 = newpoint[1] - oldpoint[1]
                    length = math.sqrt(x1 * x1 + y1 * y1)
                    _radians = math.atan2(y1, x1)
                    degrees = math.degrees(_radians)

                    print(degrees)
                    tempdegree = lastDegree - degrees
                    print(-tempdegree)
                    lastDegree = degrees

                    move_cmd = Twist()
                    move_cmd.linear.x = 0.2

                    turn_cmd = Twist()
                    turn_cmd.linear.x = 0
                    turn_cmd.angular.z = radians(-tempdegree);


                    for x in range(0, 10):
                        self.cmd_vel.publish(turn_cmd)
                        r.sleep()

                    for x in range(0, int(length/8)):
                        self.cmd_vel.publish(move_cmd)
                        r.sleep()
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
