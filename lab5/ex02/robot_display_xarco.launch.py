from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Получить путь к пакету
    pkg_share = get_package_share_directory('ex02')
    urdf_xacro_path = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    rviz_config = os.path.join(pkg_share, 'rviz', 'display.rviz')

    # ===== ОБРАБОТКА XACRO В URDF =====
    robot_description_content = Command([
        'xacro ',
        urdf_xacro_path
    ])

    # ===== УЗЕЛ: robot_state_publisher =====
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': False
        }]
    )

    # ===== УЗЕЛ: joint_state_publisher_gui =====
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    # ===== УЗЕЛ: rviz2 =====
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    # ===== ВОЗВРАТ ОПИСАНИЯ ЗАПУСКА =====
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
