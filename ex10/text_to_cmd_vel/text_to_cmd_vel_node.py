#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist

class TextToCmdVel(Node):
    def __init__(self):
        super().__init__('text_to_cmd_vel')
        
        # Создаем подписчика на текстовые команды
        self.subscription = self.create_subscription(
            String,
            'cmd_text',
            self.cmd_text_callback,
            10
        )
        
        # Создаем издателя для команд скорости
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        
        self.get_logger().info('text_to_cmd_vel node started')
        self.get_logger().info('Available commands: turn_right, turn_left, move_forward, move_backward')
    
    def cmd_text_callback(self, msg):
        command = msg.data.lower().strip()
        twist_msg = Twist()
        
        # Обрабатываем команды
        if command == 'turn_right':
            twist_msg.angular.z = -1.5  # Поворот направо
            self.get_logger().info('Turning right')
        elif command == 'turn_left':
            twist_msg.angular.z = 1.5   # Поворот налево
            self.get_logger().info('Turning left')
        elif command == 'move_forward':
            twist_msg.linear.x = 1.0    # Движение вперед
            self.get_logger().info('Moving forward')
        elif command == 'move_backward':
            twist_msg.linear.x = -1.0   # Движение назад
            self.get_logger().info('Moving backward')
        else:
            self.get_logger().warn(f'Unknown command: {command}')
            return
        
        # Публикуем команду скорости
        self.publisher.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TextToCmdVel()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
