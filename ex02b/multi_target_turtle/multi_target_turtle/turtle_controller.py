import math
import sys
import select
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from tf2_ros import TransformException

from multi_target_turtle_msg.msg import CurrentTarget


class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.switch_threshold = self.declare_parameter(
            'switch_threshold', 1.0).get_parameter_value().double_value
        self.targets = ['carrot1', 'carrot2', 'static_target']
        self.current_target_idx = 0
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.turtle_pub = self.create_publisher(Twist, 'turtle2/cmd_vel', 1)
        self.target_pub = self.create_publisher(CurrentTarget, '/current_target', 1)

        self.timer = self.create_timer(0.1, self.broadcast_timer_callback)

    def broadcast_timer_callback(self):
        current_target = self.targets[self.current_target_idx]

        if self._switch_key_pressed():
            self.current_target_idx = (self.current_target_idx + 1) % len(self.targets)
            current_target = self.targets[self.current_target_idx]
            self.get_logger().info(f'Manually switched to target: {current_target}')

        try:
            t = self.tf_buffer.lookup_transform('turtle2', current_target, rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().info(
                        f'Could not transform turtle2 to {current_target}: {ex}')
            return

        dx = t.transform.translation.x
        dy = t.transform.translation.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.switch_threshold:
            self.current_target_idx = (self.current_target_idx + 1) % len(self.targets)
            current_target = self.targets[self.current_target_idx]
            self.get_logger().info(f'Switched to target: {current_target}')

        msg = CurrentTarget()
        msg.target_name = current_target
        msg.target_x = dx
        msg.target_y = dy
        msg.distance_to_target = distance
        self.target_pub.publish(msg)

        twist = Twist()
        twist.linear.x = distance
        twist.angular.z = 2.0 *  math.atan2(dy, dx)
        self.turtle_pub.publish(twist)

    def _switch_key_pressed(self):
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline().strip()
            return line.lower() == ''


def main():
    rclpy.init()
    node = TurtleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()