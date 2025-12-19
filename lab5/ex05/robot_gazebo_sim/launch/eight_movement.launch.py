from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    pkg_share = get_package_share_directory('robot_gazebo_sim')
    xacro_path = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_path).toxml()

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    # Spawn
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'tank_robot', '-z', '0.3'],
        output='screen'
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
        ],
        output='screen'
    )

    # **Уникальный узел "восьмёрка"**
    eight_movement = Node(
        package='robot_gazebo_sim',
        executable='eight_movement',
        name='eight_movement',
        output='screen'
    )

    # RViz
    rviz_config = os.path.join(pkg_share, 'rviz', 'robot_view.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # TF дерево (для проверки)
    view_frames = Node(
        package='tf2_tools',
        executable='view_frames',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        eight_movement,  # Автономная восьмёрка!
        rviz,
        view_frames,
    ])
