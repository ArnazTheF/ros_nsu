import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'multi_target_turtle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='semar',
    maintainer_email='semarsdmi@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'target_switcher = multi_target_turtle.target_switcher:main',
            'turtle_controller = multi_target_turtle.turtle_controller:main',
            'turtle_tf2_broadcaster = multi_target_turtle.turtle_tf2_broadcaster:main',
        ],
    },
)