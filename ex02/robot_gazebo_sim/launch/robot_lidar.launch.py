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

    # **Gazebo с миром gpu_lidar_sensor.sdf (с препятствиями)**
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r gpu_lidar_sensor.sdf'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'tank_robot', '-z', '0.3'],
        output='screen'
    )

    lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'tower', 'tank_robot/tower/lidar_sensor'],
        output='screen'
    )

    # Bridge для /cmd_vel, /joint_states и **/scan**
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/model/tank_robot/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',

            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )



    # RViz с лидаром
    rviz_config = os.path.join(pkg_share, 'rviz', 'robot_lidar.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        lidar_tf,
        rviz,
    ])
