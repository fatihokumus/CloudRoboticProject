import rospy
from geometry_msgs.msg import Twist
from math import radians
import sys

try:
    import thread
except ImportError:
    import _thread as thread
import time

degree = 0

class Turn():
    def __init__(self):
        rospy.init_node('drawasquare', anonymous=False)

        rospy.on_shutdown(self.shutdown)

        self.cmd_vel = rospy.Publisher('cmd_vel_mux/input/navi', Twist, queue_size=10)

        r = rospy.Rate(5);

        turn_cmd = Twist()
        turn_cmd.linear.x = 0
        turn_cmd.angular.z = radians(float(degree));

        for x in range(0, 10):
            self.cmd_vel.publish(turn_cmd)
            r.sleep()


    def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Stop Drawing Squares")
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)



if __name__ == "__main__":
    print(sys.argv[1])
    degree = sys.argv[1]
    try:
        Turn()
    except Exception as e:
        print(e)