import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
import sys

from action_cleaning_interface.action import CleaningTask


class CleaningActionClient(Node):
    def __init__(self):
        super().__init__('cleaning_action_client')
        self._action_client = ActionClient(self, CleaningTask, 'CleaningTask')
        self.get_logger().info('Cleaning Action Client has been started')

    def send_goal(self, task_type, area_size=0.0, target_x=0.0, target_y=0.0):
        """Отправка цели на выполнение"""
        goal_msg = CleaningTask.Goal()
        goal_msg.task_type = task_type
        goal_msg.area_size = area_size
        goal_msg.target_x = target_x
        goal_msg.target_y = target_y

        self._action_client.wait_for_server()

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Обработка ответа на цель"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Обработка результата выполнения"""
        result = future.result().result
        self.get_logger().info(f'Task completed: {result.success}')
        self.get_logger().info(f'Cleaned points: {result.cleaned_points}')
        self.get_logger().info(f'Total distance: {result.total_distance:.2f}')
        
        # Завершаем работу после выполнения
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        """Обработка feedback"""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Progress: {feedback.progress_percent}%, '
            f'Cleaned points: {feedback.current_cleaned_points}, '
            f'Position: ({feedback.current_x:.2f}, {feedback.current_y:.2f})')


def main(args=None):
    rclpy.init(args=args)
    
    action_client = CleaningActionClient()
    
    # Последовательность команд: уборка квадрата 3x3 и возврат домой
    try:
        # Уборка квадрата 3x3 метра
        action_client.get_logger().info('Sending clean_square goal...')
        action_client.send_goal('clean_square', area_size=3.0)
        
        rclpy.spin(action_client)
        
    except KeyboardInterrupt:
        action_client.get_logger().info('Client interrupted')
    finally:
        if rclpy.ok():
            # После уборки квадрата возвращаемся домой
            action_client.get_logger().info('Sending return_home goal...')
            action_client.send_goal('return_home', target_x=5.5, target_y=5.5)
            rclpy.spin(action_client)


if __name__ == '__main__':
    main()