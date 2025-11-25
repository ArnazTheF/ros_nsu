import rclpy
from rclpy.node import Node
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import Twist
import math

class Turtle2Tf2Listener(Node):
    def __init__(self):
        super().__init__('turtle2_tf2_listener')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publisher = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)
        self.error_count = 0
        self.max_errors = 10
        
    def on_timer(self):
        try:
            # Пытаемся найти преобразование между turtle2 и carrot
            t = self.tf_buffer.lookup_transform(
                'turtle2',
                'carrot',
                rclpy.time.Time())
            
            # Если успешно, сбрасываем счетчик ошибок
            self.error_count = 0
            
            msg = Twist()
            scale_rotation_rate = 4.0
            scale_forward_speed = 0.5
            
            # Вычисляем угловую скорость для поворота к морковке
            msg.angular.z = scale_rotation_rate * math.atan2(
                t.transform.translation.y,
                t.transform.translation.x)
                
            # Вычисляем линейную скорость для движения к морковке
            distance = math.sqrt(
                t.transform.translation.x ** 2 +
                t.transform.translation.y ** 2)
            msg.linear.x = scale_forward_speed * distance
            
            self.publisher.publish(msg)
            self.get_logger().debug('Отправлена команда для turtle2')
            
        except TransformException as ex:
            self.error_count += 1
            if self.error_count <= self.max_errors:
                self.get_logger().info(f'Ожидание трансформаций: {ex}')
            elif self.error_count == self.max_errors + 1:
                self.get_logger().warn('Продолжаю ожидание трансформаций...')

def main():
    rclpy.init()
    node = Turtle2Tf2Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()