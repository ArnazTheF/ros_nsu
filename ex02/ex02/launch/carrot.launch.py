from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'radius',
            default_value='2.0',
            description='Радиус вращения морковки вокруг turtle1'
        ),
        DeclareLaunchArgument(
            'direction_of_rotation',
            default_value='1',
            description='Направление вращения: 1 по часовой, -1 против'
        ),
        
        # Запуск turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
        
        # Вещатель для turtle1 (запускаем сразу)
        Node(
            package='ex02',
            executable='turtle1_tf2_broadcaster',
            name='broadcaster1'
        ),
        
        # Вещатель для carrot (запускаем сразу)
        Node(
            package='ex02',
            executable='carrot_tf2_broadcaster',
            name='broadcaster2',
            parameters=[{
                'radius': LaunchConfiguration('radius'),
                'direction_of_rotation': LaunchConfiguration('direction_of_rotation')
            }]
        ),
        
        # Rviz2 (запускаем сразу)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(get_package_share_directory('ex02'), 'resource', 'carrot.rviz')]
        ),
        
        # Создание второй черепахи через сервис (с задержкой)
        TimerAction(
            period=3.0,
            actions=[
                ExecuteProcess(
                    cmd=['ros2', 'service', 'call', '/spawn', 'turtlesim/srv/Spawn', 
                         '{"x": 1.0, "y": 1.0, "theta": 0.0, "name": "turtle2"}'],
                    output='screen'
                )
            ]
        ),
        
        # Вещатель для turtle2 (запускаем с задержкой после создания черепахи)
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='ex02',
                    executable='turtle2_tf2_broadcaster',
                    name='broadcaster3'
                )
            ]
        ),
        
        # Слушатель для turtle2 (запускаем с задержкой после вещателя)
        TimerAction(
            period=7.0,
            actions=[
                Node(
                    package='ex02',
                    executable='turtle2_tf2_listener',
                    name='listener'
                )
            ]
        ),
    ])