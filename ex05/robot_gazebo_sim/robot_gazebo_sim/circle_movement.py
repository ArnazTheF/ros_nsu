#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleMovementNode(Node):
    def __init__(self):
        super().__init__('circle_movement')
        
    
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.linear_speed = 0.3  # м/с
        self.angular_speed = 0.8  # рад/с
        
        # Timer для публикации 10 Гц
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.get_logger().info('Circle movement node started! Робот поедет по кругу.')

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = self.linear_speed 
        msg.angular.z = self.angular_speed  
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CircleMovementNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
