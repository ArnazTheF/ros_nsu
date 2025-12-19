from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_gazebo_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'urdf'),
            glob(os.path.join('urdf', '*.xacro'))),
        (os.path.join('share', package_name, 'rviz'),
            glob(os.path.join('rviz', '*.rviz'))),
    ],
    entry_points={
        'console_scripts': [
            'circle_movement = robot_gazebo_sim.circle_movement:main',
            'eight_movement = robot_gazebo_sim.eight_movement:main',
        ],
    },
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='semar',
    maintainer_email='semar@example.com',
    description='Differential drive robot simulation',
    license='Apache-2.0',
)
