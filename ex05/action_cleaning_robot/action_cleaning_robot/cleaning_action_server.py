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
        self.get_logger().info('Cleaning Action Server has been started')

    def pose_callback(self, msg):
        """Сохраняем текущую позицию черепахи"""
        self.current_pose = msg
        print(self.current_pose)

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
        total_distance = 0.0
        cleaned_points = 0
        
        if goal.task_type == 'clean_square':
            # Уборка квадратной области
            side_length = goal.area_size
            sides_completed = 0
            total_sides = 4
            
            while side_length > 0:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    result.success = False
                    return result
                
                # Движение вперед на длину стороны
                success = self.move_forward(side_length, goal_handle, feedback)
                if not success:
                    result.success = False
                    return result
                
                # Поворот на 90 градусов
                self.turn(90, goal_handle, feedback)
                
                sides_completed += 1
                progress = int((sides_completed / total_sides) * 100)
                cleaned_points = int((sides_completed / total_sides) * 100)
                
                # Публикуем feedback
                feedback.progress_percent = progress
                feedback.current_cleaned_points = cleaned_points
                feedback.current_x = self.current_pose.x
                feedback.current_y = self.current_pose.y
                goal_handle.publish_feedback(feedback)
            
            total_distance = side_length * 4
            side_length-=0.1
            cleaned_points = 100
            
        elif goal.task_type == 'return_home':
            # Возвращение в домашнюю позицию
            target_x = goal.target_x
            target_y = goal.target_y
            
            success = self.move_to_position(target_x, target_y, goal_handle, feedback)
            total_distance = self.calculate_distance(
                start_pose.x, start_pose.y, target_x, target_y)
            cleaned_points = 0
            
            if success:
                feedback.progress_percent = 100
                feedback.current_cleaned_points = 0
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
        result.cleaned_points = cleaned_points
        result.total_distance = total_distance
        
        self.get_logger().info('Task completed successfully')
        return result

    def move_forward(self, distance, goal_handle, feedback):
        """Движение вперед на указанное расстояние"""
        if self.current_pose is None:
            return False
        
        start_x, start_y = self.current_pose.x, self.current_pose.y
        print(start_x, start_y)
        distance_traveled = 0.0
        
        while distance_traveled < distance and rclpy.ok():
            if goal_handle.is_cancel_requested:
                return False
            
            rclpy.spin_once(self, timeout_sec=0.01)
            # Публикуем команду движения
            twist = Twist()
            twist.linear.x = 0.5  # Постоянная скорость
            self.vel_publisher.publish(twist)
            
            time.sleep(0.2)
            
            # Обновляем пройденное расстояние
            current_distance = math.sqrt(
                (self.current_pose.x - start_x)**2 + 
                (self.current_pose.y - start_y)**2)
            distance_traveled = current_distance
            print(self.current_pose.x, self.current_pose.y)
            
            # Публикуем feedback
            progress = int((distance_traveled / distance) * 25)  # 25% за сторону
            feedback.progress_percent = min(100, progress)
            feedback.current_cleaned_points = progress
            feedback.current_x = self.current_pose.x
            feedback.current_y = self.current_pose.y
            goal_handle.publish_feedback(feedback)
            
            time.sleep(0.1)
        
        # Останавливаемся
        twist = Twist()
        self.vel_publisher.publish(twist)
        time.sleep(0.5)
        
        return True

    def turn(self, angle_degrees, goal_handle, feedback):
        """Поворот на указанный угол в градусах"""
        if self.current_pose is None:
            return
        
        target_angle = self.current_pose.theta + math.radians(angle_degrees)
        
        while abs(self.current_pose.theta - target_angle) > 0.1 and rclpy.ok():
            if goal_handle.is_cancel_requested:
                return
            rclpy.spin_once(self, timeout_sec=0.01)
            # Публикуем команду поворота
            twist = Twist()
            twist.angular.z = 0.5 if angle_degrees > 0 else -0.5
            self.vel_publisher.publish(twist)
            
            time.sleep(0.1)
        
        # Останавливаемся
        twist = Twist()
        self.vel_publisher.publish(twist)
        time.sleep(0.5)

    def move_to_position(self, target_x, target_y, goal_handle, feedback):
        """Движение к указанной позиции"""
        if self.current_pose is None:
            return False
        
        total_distance = self.calculate_distance(
            self.current_pose.x, self.current_pose.y, target_x, target_y)
        
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
            
            # Публикуем feedback
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