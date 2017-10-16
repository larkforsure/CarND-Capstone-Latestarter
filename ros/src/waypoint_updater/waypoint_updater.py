#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint

import math
import tf

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below

	self.pose = None        
        self.wpts = None
        self.future_waypoints = None

        rospy.spin()

    def pose_cb(self, msg):
        quaternion = (msg.pose.orientation.x,
                        msg.pose.orientation.y,
                        msg.pose.orientation.z,
                        msg.pose.orientation.w)
        euler = tf.transformations.euler_from_quaternion(quaternion)
        car_roll = euler[0]
        car_pitch = euler[1]
        car_yaw = euler[2]
        car_x = msg.pose.position.x
        car_y = msg.pose.position.y
        self.pose = [car_x, car_y, car_yaw]     
        rospy.loginfo("curent pose  (%s, %s, %s)", car_x, car_y, car_yaw)
        rospy.loginfo("future waypoints %s", self.wpts.waypoints[0])
        future_wpts = []
        if (self.wpts is not None):
		for pt in self.wpts.waypoints:
			if car_x <= pt.pose.pose.position.x:
                                future_wpts.append(pt)
                                if len(future_wpts) > (LOOKAHEAD_WPS - 1):
                                        self.future_waypoints = future_wpts
                                        break
                now = rospy.get_rostime()
                final_pts = Lane()
                final_pts.header.stamp.secs = now.secs
                final_pts.header.stamp.nsecs = now.nsecs
                final_pts.header.frame_id = "Our World"
                final_pts.waypoints = self.future_waypoints
                self.final_waypoints_pub.publish(final_pts)

        return

    def waypoints_cb(self, waypoints):
        if (self.wpts is None):
                self.wpts = waypoints
                rospy.loginfo("Obtained Base_Waypoints %s", len(self.wpts.waypoints))
	return

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
