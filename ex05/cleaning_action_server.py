import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
import math
import time

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from action_cleaning_interface.action import CleaningTask


class CleaningActionServer(Node):
    def __init__(self):
        super().__init__('cleaning_action_server')
        
        # Публикатор для управления движением черепахи
        self.vel_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Подписка на позицию черепахи
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10)
        
        # Сервер действий
        self._action_server = ActionServer(
            self,
            CleaningTask,
            'CleaningTask',
            self.execute_callback)
        
        # Текущая позиция черепахи
        self.current_pose = None
        self.current_direction = 'right'  # Начальное направление
        self.get_logger().info('Cleaning Action Server has been started')

    def pose_callback(self, msg):
        """Сохраняем текущую позицию черепахи"""
        self.current_pose = msg

    def execute_callback(self, goal_handle):
        """Обработчик выполнения целей"""
        self.get_logger().info(f'Executing task: {goal_handle.request.task_type}')
        
        goal = goal_handle.request
        result = CleaningTask.Result()
        feedback = CleaningTask.Feedback()
        
        # Ожидаем получение первой позиции
        while self.current_pose is None and rclpy.ok():
            self.get_logger().info('Waiting for pose...', once=True)
            time.sleep(0.1)
        
        start_pose = self.current_pose
        
        if goal.task_type == 'clean_square':
            # Уборка квадратной области - ИСПРАВЛЕННАЯ ЛОГИКА
            area_size = goal.area_size
            step_size = 0.1  # Размер шага для спирали
            
            # Рассчитываем общее количество итераций на основе размера области
            total_iterations = int(area_size / step_size) * 4
            iterations_completed = 0
            
            current_size = area_size
            
            # Начинаем с направления вправо
            self.current_direction = 'right'
            
            # Двигаемся по спирали, уменьшая размер на каждой итерации
            while current_size > 0 and rclpy.ok():
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    result.success = False
                    return result
                
                # Движение вперед на ТЕКУЩУЮ длину
                success = self.move_forward(current_size, goal_handle, feedback)
                if not success:
                    result.success = False
                    return result
                
                # Поворот в следующее направление по часовой стрелке
                next_direction = self.get_next_direction_clockwise()
                self.turn_to_direction(next_direction, goal_handle, feedback)
                self.current_direction = next_direction
                
                iterations_completed += 1
                
                # Расчет прогресса на основе выполненных итераций
                progress = int((iterations_completed / total_iterations) * 100)
                cleaned_points = progress
                
                # Публикуем feedback
                feedback.progress_percent = progress
                feedback.current_cleaned_points = cleaned_points
                feedback.current_x = self.current_pose.x
                feedback.current_y = self.current_pose.y
                goal_handle.publish_feedback(feedback)
                
                # Уменьшаем размер для следующей итерации
                current_size -= step_size
                self.get_logger().info(f'Current size: {current_size:.2f}, Direction: {self.current_direction}, Progress: {progress}%')
            
            total_distance = area_size * total_iterations / 4
            
        elif goal.task_type == 'return_home':
            # Возвращение в домашнюю позицию
            target_x = goal.target_x
            target_y = goal.target_y
            
            success = self.move_to_position(target_x, target_y, goal_handle, feedback)
            total_distance = self.calculate_distance(
                start_pose.x, start_pose.y, target_x, target_y)
            
            if success:
                feedback.progress_percent = 100
                feedback.current_cleaned_points = 100
                goal_handle.publish_feedback(feedback)
            else:
                result.success = False
                return result
        else:
            self.get_logger().error(f'Unknown task type: {goal.task_type}')
            result.success = False
            return result
        
        # Возвращаем успешный результат
        goal_handle.succeed()
        result.success = True
        result.cleaned_points = 100
        result.total_distance = total_distance
        
        self.get_logger().info('Task completed successfully')
        return result

    def get_next_direction_clockwise(self):
        """Получить следующее направление по часовой стрелке"""
        directions = ['right', 'down', 'left', 'up']
        current_index = directions.index(self.current_direction)
        next_index = (current_index + 1) % 4
        return directions[next_index]

    def turn_to_direction(self, target_direction, goal_handle, feedback):
        """Поворот к указанному направлению (right, up, left, down)"""
        if self.current_pose is None:
            return
        
        # Углы для каждого направления в радианах
        direction_angles = {
            'right': 0.0,
            'up': math.pi / 2,
            'left': math.pi,
            'down': 3 * math.pi / 2
        }
        
        target_angle = direction_angles[target_direction]
        current_angle = self.current_pose.theta
        
        # Нормализуем углы в диапазон [0, 2π]
        current_angle = current_angle % (2 * math.pi)
        if current_angle < 0:
            current_angle += 2 * math.pi
        
        # Вычисляем минимальную разницу углов
        angle_diff = target_angle - current_angle
        
        # Корректируем разницу для кратчайшего пути
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        self.get_logger().info(f'Turning from {self.current_direction} to {target_direction}, angle diff: {math.degrees(angle_diff):.1f}°')
        
        # Выполняем поворот
        angular_speed = 0.5
        angle_tolerance = 0.05
        
        start_time = time.time()
        timeout = 5.0
        
        while rclpy.ok() and (time.time() - start_time) < timeout:
            if goal_handle.is_cancel_requested:
                return
            
            rclpy.spin_once(self, timeout_sec=0.01)
            
            if self.current_pose is None:
                continue
            
            current_angle = self.current_pose.theta % (2 * math.pi)
            if current_angle < 0:
                current_angle += 2 * math.pi
            
            current_diff = target_angle - current_angle
            if current_diff > math.pi:
                current_diff -= 2 * math.pi
            elif current_diff < -math.pi:
                current_diff += 2 * math.pi
            
            if abs(current_diff) < angle_tolerance:
                break
            
            twist = Twist()
            if current_diff > 0:
                twist.angular.z = angular_speed
            else:
                twist.angular.z = -angular_speed
            
            self.vel_publisher.publish(twist)
            time.sleep(0.05)
        
        # Останавливаемся
        twist = Twist()
        self.vel_publisher.publish(twist)
        time.sleep(0.2)

    def move_forward(self, distance, goal_handle, feedback):
        """Движение вперед на указанное расстояние"""
        if self.current_pose is None:
            return False
        
        start_x, start_y = self.current_pose.x, self.current_pose.y
        distance_traveled = 0.0
        
        # Устанавливаем скорость
        speed = 0.5
        
        while distance_traveled < distance and rclpy.ok():
            if goal_handle.is_cancel_requested:
                return False
            
            rclpy.spin_once(self, timeout_sec=0.01)
            
            # Публикуем команду движения
            twist = Twist()
            twist.linear.x = speed
            self.vel_publisher.publish(twist)
            
            time.sleep(0.1)
            
            # Обновляем пройденное расстояние
            if self.current_pose:
                current_distance = math.sqrt(
                    (self.current_pose.x - start_x)**2 + 
                    (self.current_pose.y - start_y)**2)
                distance_traveled = current_distance
            
            time.sleep(0.05)
        
        # Останавливаемся
        twist = Twist()
        self.vel_publisher.publish(twist)
        time.sleep(0.1)
        
        return True

    def move_to_position(self, target_x, target_y, goal_handle, feedback):
        """Движение к указанной позиции"""
        if self.current_pose is None:
            return False
        
        total_distance = self.calculate_distance(
            self.current_pose.x, self.current_pose.y, target_x, target_y)
        distance_traveled = 0.0
        
        while (self.calculate_distance(self.current_pose.x, self.current_pose.y, target_x, target_y) > 0.1 
               and rclpy.ok()):
            if goal_handle.is_cancel_requested:
                return False
            
            # Вычисляем направление к цели
            angle_to_target = math.atan2(
                target_y - self.current_pose.y, 
                target_x - self.current_pose.x)
            
            # Поворачиваем в направлении цели
            angle_diff = angle_to_target - self.current_pose.theta
            if abs(angle_diff) > 0.1:
                twist = Twist()
                twist.angular.z = 0.5 if angle_diff > 0 else -0.5
                self.vel_publisher.publish(twist)
            else:
                # Двигаемся вперед
                twist = Twist()
                twist.linear.x = 0.5
                self.vel_publisher.publish(twist)
            
            # Обновляем прогресс
            current_distance = self.calculate_distance(
                self.current_pose.x, self.current_pose.y, target_x, target_y)
            progress = int(((total_distance - current_distance) / total_distance) * 100)
            feedback.progress_percent = progress
            feedback.current_cleaned_points = 0
            feedback.current_x = self.current_pose.x
            feedback.current_y = self.current_pose.y
            goal_handle.publish_feedback(feedback)
            
            time.sleep(0.1)
        
        # Останавливаемся
        twist = Twist()
        self.vel_publisher.publish(twist)
        return True

    def calculate_distance(self, x1, y1, x2, y2):
        """Вычисление расстояния между двумя точками"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def main(args=None):
    rclpy.init(args=args)
    cleaning_action_server = CleaningActionServer()
    
    try:
        rclpy.spin(cleaning_action_server)
    except KeyboardInterrupt:
        pass
    finally:
        cleaning_action_server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()