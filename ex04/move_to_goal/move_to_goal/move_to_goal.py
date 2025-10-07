import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import sys

class MoveToGoal(Node):
    def __init__(self):
        super().__init__('move_to_goal')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)
        self.current_pose = None
        if len(sys.argv) != 4:
            self.get_logger().error('Usage: ros2 run move_to_goal move_to_goal x y theta')
            rclpy.shutdown()
            return
        try:
            self.goal_x = float(sys.argv[1])
            self.goal_y = float(sys.argv[2])
            self.goal_theta = float(sys.argv[3])
        except ValueError:
            self.get_logger().error('Invalid float arguments for x, y, theta')
            rclpy.shutdown()
            return
        self.timer = self.create_timer(0.1, self.control_loop)

    def pose_callback(self, msg):
        self.current_pose = msg

    def control_loop(self):
        if self.current_pose is None:
            return
        dx = self.goal_x - self.current_pose.x
        dy = self.goal_y - self.current_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        twist = Twist()
        if distance > 0.1:
            angle_to_goal = math.atan2(dy, dx)
            angle_error = angle_to_goal - self.current_pose.theta
            angle_error = (angle_error + math.pi) % (2 * math.pi) - math.pi
            # Reduce linear speed when angle error is large to avoid arcs
            linear_factor = 1 - abs(angle_error) / math.pi
            twist.linear.x = 1.0 * distance * linear_factor
            twist.angular.z = 4.0 * angle_error
        else:
            theta_error = self.goal_theta - self.current_pose.theta
            theta_error = (theta_error + math.pi) % (2 * math.pi) - math.pi
            if abs(theta_error) > 0.1:
                twist.linear.x = 0.0
                twist.angular.z = 2.0 * theta_error
            else:
                self.get_logger().info('Goal reached')
                rclpy.shutdown()
                return
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = MoveToGoal()
    rclpy.spin(node)

if __name__ == '__main__':
    main()