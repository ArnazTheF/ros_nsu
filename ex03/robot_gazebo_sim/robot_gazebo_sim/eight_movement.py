#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class EightMovementNode(Node):
    def __init__(self):
        super().__init__('eight_movement')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Состояния для восьмёрки
        self.states = ['forward_left', 'forward_right']  # вперёд-левый поворот, вперёд-правый поворот
        self.state_index = 0
        self.start_time = time.time()
        self.duration = 3.0  # 3 секунды на состояние
        
        self.linear_speed = 0.4
        self.angular_left = 0.6
        self.angular_right = -0.6
        
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('Eight movement started! Робот поедет по восьмёрке.')

    def timer_callback(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Переключаем состояние каждые 3 сек
        if elapsed > self.duration:
            self.state_index = (self.state_index + 1) % len(self.states)
            self.start_time = current_time
            self.get_logger().info(f'Switch to state: {self.states[self.state_index]}')
        
        msg = Twist()
        if self.states[self.state_index] == 'forward_left':
            msg.linear.x = self.linear_speed
            msg.angular.z = self.angular_left  # поворот влево
        else:  # forward_right
            msg.linear.x = self.linear_speed
            msg.angular.z = self.angular_right  # поворот вправо
            
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = EightMovementNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
