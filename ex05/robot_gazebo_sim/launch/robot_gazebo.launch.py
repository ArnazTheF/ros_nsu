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

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'diff_drive_robot', '-z', '0.3'],
        output='screen'
    )

    # ВАЖНО: направления bridge (] = ROS->GZ, [ = GZ->ROS)  [web:105]
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # ROS -> Gazebo (заканчивается на ])
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            
            # Gazebo -> ROS (начинается с [ )
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )


    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'rviz', 'robot_view.rviz')],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        rviz_node
    ])
